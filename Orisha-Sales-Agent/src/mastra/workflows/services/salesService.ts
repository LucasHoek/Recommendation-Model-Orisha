import { spawn } from "child_process";
import path from "path";

export async function getHybridTopN({ klantcode, topn }) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, "python/recommender_bridge.py");

    const py = spawn("python3", [scriptPath, klantcode.toString(), topn.toString()]);

    let output = "";
    let errorOutput = "";

    py.stdout.on("data", (data) => (output += data.toString()));
    py.stderr.on("data", (data) => (errorOutput += data.toString()));

    py.on("close", () => {
      if (errorOutput) console.error(errorOutput);

      try {
        resolve(JSON.parse(output));
      } catch (err) {
        reject(err);
      }
    });
  });
}
