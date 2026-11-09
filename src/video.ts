/** Convert a trusted YouTube embed URL into a direct source-page link. */
export function youtubeWatchUrl(videoUrl?: string): string | undefined {
  if (!videoUrl) return undefined;
  try {
    const url = new URL(videoUrl);
    const videoId = url.pathname.match(/^\/embed\/([A-Za-z0-9_-]+)$/)?.[1];
    if (url.hostname !== 'www.youtube.com' || !videoId) return videoUrl;
    return `https://www.youtube.com/watch?v=${videoId}`;
  } catch {
    return videoUrl;
  }
}
