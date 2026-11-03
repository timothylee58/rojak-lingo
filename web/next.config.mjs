/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
  // Project Pages serves the site under /rojak-lingo; asset URLs need the prefix.
  // Local dev and root-domain hosts build without it.
  basePath: process.env.PAGES_BASE_PATH === "true" ? "/rojak-lingo" : "",
};

export default nextConfig;
