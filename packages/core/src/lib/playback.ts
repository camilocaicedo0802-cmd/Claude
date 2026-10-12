"use client";

/**
 * Keeps a single preview video playing at a time across the page,
 * so hover previews and carousels never stack decoders.
 */
let current: HTMLVideoElement | null = null;

export function playExclusive(video: HTMLVideoElement) {
  if (current && current !== video) current.pause();
  current = video;
  const attempt = video.play();
  if (attempt) attempt.catch(() => {});
}

export function release(video: HTMLVideoElement) {
  video.pause();
  if (current === video) current = null;
}

export function pauseAll() {
  current?.pause();
  current = null;
}
