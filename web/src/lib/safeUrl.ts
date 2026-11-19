export function safeGithubUrl(url: string | null | undefined): string {
  try {
    const u = new URL(url ?? "");
    if (
      u.protocol === "https:" &&
      (u.hostname === "github.com" || u.hostname === "www.github.com")
    ) {
      return u.href;
    }
  } catch {
    // invalid URL, fall through
  }
  return "#";
}