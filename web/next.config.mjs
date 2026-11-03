/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  // Project Pages serves the site under /rojak-lingo; asset URLs need the prefix.
  // Local dev and root-domain hosts build without it.
  basePath: process.env.NEXT_PUBLIC_BASE_PATH ?? "",
};

export default nextConfig;
