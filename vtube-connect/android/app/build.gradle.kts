plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }

android { namespace = "com.vtube.connect"; compileSdk = 35
    defaultConfig { applicationId = "com.vtube.connect"; minSdk = 26; targetSdk = 35; versionCode = 1; versionName = "0.2.0-alpha" }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.activity:activity-ktx:1.9.3")
    implementation("androidx.camera:camera-core:1.4.1")
    implementation("androidx.camera:camera-camera2:1.4.1")
    implementation("androidx.camera:camera-lifecycle:1.4.1")
    implementation("androidx.camera:camera-view:1.4.1")
}
