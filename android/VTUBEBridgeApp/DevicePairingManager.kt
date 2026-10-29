package com.vtube.bridge

import android.app.Service
import android.content.Intent
import android.os.Binder
import android.os.IBinder

class BridgeService : Service() {
    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): BridgeService = this@BridgeService
    }

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    fun connectToDesktop(host: String, token: String): Boolean {
        // Connect to VTUBE OS host over network.
        return host.isNotBlank() && token.isNotBlank()
    }
}
