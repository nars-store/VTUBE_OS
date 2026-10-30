"""Compatibility wrapper for avatar asset loading.

This module exposes the loader used throughout the VTuber runtime.
"""
from __future__ import annotations

from vtube_avatar_loader_real import AvatarAssetLoader


__all__ = ["AvatarAssetLoader"]


if __name__ == "__main__":
    print(AvatarAssetLoader().snapshot())
