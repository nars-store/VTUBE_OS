package com.vtube.connect

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import java.io.BufferedInputStream
import java.io.BufferedOutputStream
import java.net.ServerSocket
import java.net.Socket
import java.net.URLDecoder
import java.util.concurrent.atomic.AtomicBoolean

class PhoneMediaServer(private val token: String) {
    private var server: ServerSocket? = null
    private val running = AtomicBoolean(false)
    @Volatile private var audioRecord: AudioRecord? = null
    @Volatile private var latestCommand: String = "none"
    fun start() { if (running.getAndSet(true)) return; Thread { try { server = ServerSocket(8765); while (running.get()) { val s = server!!.accept(); Thread { handle(s) }.start() } } catch (_: Exception) {} }.start() }
    fun stopServer() { running.set(false); try { server?.close() } catch (_: Exception) {}; try { audioRecord?.stop(); audioRecord?.release() } catch (_: Exception) {}; audioRecord = null }
    private fun handle(socket: Socket) {
        socket.use { s ->
            try {
                s.soTimeout = 5000
                val input = BufferedInputStream(s.getInputStream()); val output = BufferedOutputStream(s.getOutputStream())
                val request = readLine(input) ?: return
                val path = request.split(" ").getOrNull(1) ?: "/"
                val headers = mutableMapOf<String,String>()
                while (true) { val line = readLine(input) ?: break; if (line.isEmpty()) break; val i=line.indexOf(':'); if(i>0) headers[line.substring(0,i).trim().lowercase()]=line.substring(i+1).trim() }
                val query = path.substringAfter('?', "").split('&').mapNotNull { val a=it.split('=',limit=2); if(a.size==2) URLDecoder.decode(a[0],"UTF-8") to URLDecoder.decode(a[1],"UTF-8") else null }.toMap()
                if (query["token"] != token) { write(output, "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"); return }
                when (path.substringBefore('?')) {
                    "/status" -> { val body="{\"status\":\"ok\",\"command\":\"$latestCommand\"}".toByteArray(); write(output,"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: ${body.size}\r\nConnection: close\r\n\r\n"); output.write(body); output.flush() }
                    "/control" -> { latestCommand=query["command"] ?: "none"; val body="OK $latestCommand".toByteArray(); write(output,"HTTP/1.1 200 OK\r\nContent-Length: ${body.size}\r\nConnection: close\r\n\r\n"); output.write(body); output.flush() }
                    "/camera.mjpeg" -> { write(output,"HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=frame\r\nCache-Control: no-cache\r\nConnection: close\r\n\r\n"); while(running.get() && !s.isClosed) { val frame=latestJpeg; if(frame!=null) { output.write("--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ${frame.size}\r\n\r\n".toByteArray()); output.write(frame); output.write("\r\n".toByteArray()); output.flush() }; Thread.sleep(40) } }
                    "/audio.pcm" -> streamAudio(output)
                    else -> { val body="VTUBE Connect local prototype".toByteArray(); write(output,"HTTP/1.1 200 OK\r\nContent-Length: ${body.size}\r\nConnection: close\r\n\r\n"); output.write(body); output.flush() }
                }
            } catch (_: Exception) {}
        }
    }
    private fun streamAudio(out: BufferedOutputStream) {
        val rate=16000; val min=AudioRecord.getMinBufferSize(rate,AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT).coerceAtLeast(4096)
        val rec=AudioRecord(MediaRecorder.AudioSource.MIC,rate,AudioFormat.CHANNEL_IN_MONO,AudioFormat.ENCODING_PCM_16BIT,min); audioRecord=rec
        write(out,"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nX-Audio-Format: s16le;rate=16000;channels=1\r\nConnection: close\r\n\r\n"); rec.startRecording(); val buf=ByteArray(min)
        try { while(running.get()) { val n=rec.read(buf,0,buf.size); if(n>0) { out.write(buf,0,n); out.flush() } } } finally { try { rec.stop(); rec.release() } catch (_:Exception) {}; audioRecord=null }
    }
    private fun readLine(input: BufferedInputStream): String? { val b=java.io.ByteArrayOutputStream(); while(true) { val c=input.read(); if(c<0) return if(b.size()>0) b.toString(Charsets.UTF_8.name()) else null; if(c==10) break; if(c!=13) b.write(c); if(b.size()>8192) return null }; return b.toString(Charsets.UTF_8.name()) }
    private fun write(out: BufferedOutputStream, text:String) { out.write(text.toByteArray()); out.flush() }
    companion object { @Volatile var latestJpeg: ByteArray? = null }
}
