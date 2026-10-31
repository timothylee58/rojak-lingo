import type { NextConfig } from "next";

// Static export: the leaderboard is plain HTML built from results/leaderboard.json.
const config: NextConfig = { output: "export" };

export default config;
