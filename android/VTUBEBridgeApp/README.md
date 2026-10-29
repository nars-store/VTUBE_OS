package com.vtube.bridge

class DevicePairingManager {
    fun generatePairToken(deviceName: String): String {
        return "vtube-${deviceName.lowercase().replace(" ", "-")}-token"
    }

    fun validatePairToken(token: String): Boolean {
        return token.startsWith("vtube-") && token.endsWith("-token")
    }
}
