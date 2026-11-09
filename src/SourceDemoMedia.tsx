type Props = { src: string; title: string; mediaType: 'gif' | 'mp4' };

/** Plays original ASLU-hosted demo media without embedding the YouTube player chrome. */
export default function SourceDemoMedia({ src, title, mediaType }: Props) {
  if (mediaType === 'mp4') {
    return <video className="source-demo-asset" src={src} title={title} autoPlay muted loop playsInline aria-label={title}/>;
  }
  return <img className="source-demo-asset" src={src} alt={title} loading="eager" decoding="async"/>;
}
