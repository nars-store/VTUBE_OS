package com.vtube.connect

import android.Manifest
import android.content.pm.PackageManager
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import java.net.Inet4Address
import java.net.NetworkInterface
import java.security.SecureRandom
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    private lateinit var status: TextView
    private lateinit var preview: PreviewView
    private var server: PhoneMediaServer? = null
    private var pairToken: String? = null
    private val executor = Executors.newSingleThreadExecutor()
    private val screenCapture = registerForActivityResult(StartActivityForResult()) { result ->
        val data = result.data
        if (result.resultCode == RESULT_OK && data != null) {
            val service = android.content.Intent(this, ScreenCaptureService::class.java)
                .putExtra(ScreenCaptureService.EXTRA_RESULT_CODE, result.resultCode)
                .putExtra(ScreenCaptureService.EXTRA_RESULT_DATA, data)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) ContextCompat.startForegroundService(this, service)
            else startService(service)
            val token = pairToken
            val ip = localIp()
            status.text = if (token != null && ip != null) {
                "Permintaan screen share dikirim.\nJika foreground notification muncul, stream tersedia di:\nhttp://$ip:8765/screen.mjpeg?token=$token\nStop / privacy untuk menghentikan."
            } else {
                "Screen share aktif. Pair code atau alamat IP belum tersedia."
            }
        } else {
            status.text = "Izin screen share dibatalkan. Tidak ada layar yang dikirim."
        }
    }
    private val permissions = registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { result ->
        if (result[Manifest.permission.CAMERA] == true) startCamera()
        if (result[Manifest.permission.RECORD_AUDIO] == true) status.text = "Mikrofon diizinkan. Audio endpoint aktif saat server lokal berjalan."
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(24, 28, 24, 24); setBackgroundColor(0xFF0B0D14.toInt()) }
        val title = TextView(this).apply { text = "VTUBE CONNECT"; textSize = 26f; setTextColor(0xFFF2F4FF.toInt()) }
        val subtitle = TextView(this).apply { text = "Phone camera · microphone · screen share · local network"; textSize = 14f; setTextColor(0xFF9BA4BD.toInt()) }
        preview = PreviewView(this).apply { implementationMode = PreviewView.ImplementationMode.COMPATIBLE }
        status = TextView(this).apply { text = "Tekan Start untuk meminta izin kamera/mikrofon."; textSize = 14f; setTextColor(0xFF64E6F2.toInt()); setPadding(0, 14, 0, 14) }
        val start = Button(this).apply { text = "Start camera + local server"; setOnClickListener { askPermissionsAndStart() } }
        val shareScreen = Button(this).apply { text = "Share phone screen"; setOnClickListener { requestScreenCapture() } }
        val stop = Button(this).apply { text = "Stop / privacy"; setOnClickListener { stopAll(); status.text = "Kamera dan server dihentikan." } }
        val remote = Button(this).apply { text = "Send test remote command"; setOnClickListener { Toast.makeText(this@MainActivity, "Pairing/control endpoint is local prototype only.", Toast.LENGTH_LONG).show() } }
        root.addView(title); root.addView(subtitle); root.addView(preview, LinearLayout.LayoutParams(-1, 0, 1f)); root.addView(status); root.addView(start); root.addView(shareScreen); root.addView(stop); root.addView(remote)
        setContentView(root)
    }

    private fun askPermissionsAndStart() {
        val needed = arrayOf(Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO).filter { ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }
        if (needed.isNotEmpty()) permissions.launch(needed.toTypedArray()) else { startCamera(); startServer() }
    }

    private fun startCamera() {
        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            try {
                val provider = future.get(); val previewUseCase = androidx.camera.core.Preview.Builder().build()
                previewUseCase.setSurfaceProvider(preview.surfaceProvider)
                val analysis = ImageAnalysis.Builder().setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST).build()
                analysis.setAnalyzer(executor) { image -> PhoneMediaServer.latestJpeg = imageToJpeg(image); image.close() }
                provider.unbindAll(); provider.bindToLifecycle(this, CameraSelector.DEFAULT_FRONT_CAMERA, previewUseCase, analysis)
                startServer()
            } catch (e: Exception) { status.text = "Camera error: ${e.message}" }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun imageToJpeg(image: ImageProxy): ByteArray? {
        return try {
            val y = image.planes[0].buffer; val u = image.planes[1].buffer; val v = image.planes[2].buffer
            val ySize = y.remaining(); val uSize = u.remaining(); val vSize = v.remaining()
            val nv21 = ByteArray(ySize + uSize + vSize)
            y.get(nv21, 0, ySize); v.get(nv21, ySize, vSize); u.get(nv21, ySize + vSize, uSize)
            val yuv = android.graphics.YuvImage(nv21, android.graphics.ImageFormat.NV21, image.width, image.height, null)
            val out = java.io.ByteArrayOutputStream(); yuv.compressToJpeg(android.graphics.Rect(0,0,image.width,image.height), 75, out); out.toByteArray()
        } catch (_: Exception) { null }
    }

    private fun startServer() {
        if (server != null) return
        val token = (1..6).map { "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"[SecureRandom().nextInt(32)] }.joinToString("")
        pairToken = token
        server = PhoneMediaServer(token).also { it.start() }
        val ip = localIp() ?: "IP HP tidak ditemukan"
        status.text = "Server lokal aktif\nPair code: $token\nCamera MJPEG: http://$ip:8765/camera.mjpeg?token=$token\nAudio PCM: http://$ip:8765/audio.pcm?token=$token\nScreen MJPEG: http://$ip:8765/screen.mjpeg?token=$token\nLaptop dan HP harus di Wi-Fi yang sama."
    }

    private fun requestScreenCapture() {
        if (server == null) {
            status.text = "Tekan Start camera + local server dahulu, lalu pilih Share phone screen."
            return
        }
        val manager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        screenCapture.launch(manager.createScreenCaptureIntent())
    }

    private fun localIp(): String? = try {
        NetworkInterface.getNetworkInterfaces().toList().flatMap { it.inetAddresses.toList() }.firstOrNull { it is Inet4Address && !it.isLoopbackAddress && it.hostAddress?.startsWith("169.254.") == false }?.hostAddress
    } catch (_: Exception) { null }

    private fun stopAll() {
        try { ProcessCameraProvider.getInstance(this).get().unbindAll() } catch (_: Exception) {}
        stopService(android.content.Intent(this, ScreenCaptureService::class.java))
        server?.stopServer(); server = null; pairToken = null
    }
    override fun onDestroy() { stopAll(); executor.shutdown(); super.onDestroy() }
}
