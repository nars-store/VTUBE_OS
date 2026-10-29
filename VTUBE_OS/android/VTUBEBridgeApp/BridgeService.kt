package com.vtube.bridge

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class PairingManager(
    private val host: String,
    private val client: OkHttpClient = OkHttpClient()
) {
    private val httpBase = "http://$host:9000"

    fun requestPairing(
        deviceId: String,
        deviceName: String,
        capabilities: List<String>,
        fingerprint: String
    ): PairingResponse {
        val payload = JSONObject().apply {
            put("device_id", deviceId)
            put("device_name", deviceName)
            put("capabilities", JSONObject.wrap(capabilities))
            put("fingerprint", fingerprint)
        }.toString()

        val request = Request.Builder()
            .url("$httpBase/api/pair/request")
            .post(payload.toRequestBody("application/json; charset=utf-8".toMediaType()))
            .build()

        val response = client.newCall(request).execute()
        val body = response.body?.string() ?: "{}"
        val json = JSONObject(body)

        return PairingResponse(
            pairId = json.optString("pair_id"),
            challenge = json.optString("challenge"),
            nonce = json.optString("nonce")
        )
    }

    fun confirmPairing(
        pairId: String,
        challenge: String,
        deviceId: String,
        fingerprint: String
    ): PairingResult {
        val payload = JSONObject().apply {
            put("pair_id", pairId)
            put("challenge", challenge)
            put("device_id", deviceId)
            put("fingerprint", fingerprint)
        }.toString()

        val request = Request.Builder()
            .url("$httpBase/api/pair/confirm")
            .post(payload.toRequestBody("application/json; charset=utf-8".toMediaType()))
            .build()

        val response = client.newCall(request).execute()
        val body = response.body?.string() ?: "{}"
        val json = JSONObject(body)

        return PairingResult(
            status = json.optString("status"),
            sessionKey = json.optString("session_key"),
            deviceId = json.optString("device_id")
        )
    }
}

data class PairingResponse(
    val pairId: String,
    val challenge: String,
    val nonce: String
)

data class PairingResult(
    val status: String,
    val sessionKey: String,
    val deviceId: String
)
