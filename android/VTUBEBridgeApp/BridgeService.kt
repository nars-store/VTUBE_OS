package com.vtube.bridge

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val permissions = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.INTERNET
        )

        if (!hasPermissions(permissions)) {
            ActivityCompat.requestPermissions(this, permissions, 1001)
        }

        val serviceIntent = Intent(this, BridgeService::class.java)
        startService(serviceIntent)
    }

    private fun hasPermissions(permissions: Array<String>): Boolean {
        return permissions.all {
            checkSelfPermission(it) == PackageManager.PERMISSION_GRANTED
        }
    }
}
