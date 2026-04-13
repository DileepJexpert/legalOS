/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    externalDir: true
  },
  transpilePackages: ["@legalos/contracts", "@legalos/ui"],
  env: {
    // Expose BYPASS_AUTH to the browser bundle so the login form can
    // skip itself when running in no-auth local dev mode.
    NEXT_PUBLIC_BYPASS_AUTH: process.env.BYPASS_AUTH ?? "false"
  }
};

export default nextConfig;
