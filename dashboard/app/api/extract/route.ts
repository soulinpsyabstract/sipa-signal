import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'node:child_process';

export async function POST(req: NextRequest) {
  try {
    const { transcript } = await req.json();

    if (!transcript) {
      return NextResponse.json({ kept: "", dropped: "", noiseScore: 0 });
    }

    return new Promise((resolve) => {
      // Spawn python and run Aelin's exact extract function
      const pythonProcess = spawn('python', [ // nosonar
        '-c', `
import sys, json, os
sys.path.append(os.path.abspath('..'))
from sipa_signal.extract import extract

try:
    raw_text = sys.stdin.read()
    
    # Run Aelin's extraction pipeline
    card = extract(raw_text)
    data = card.to_dict()
    
    # Format the data for the React frontend
    output = {
        "kept": " ".join(data["kept_sentences"]),
        "dropped": "\\n\\n".join(data["dropped_sentences"]),
        "noiseScore": round(data["noise_ratio"] * 100)
    }
    print(json.dumps(output))
except Exception as e:
    print(json.dumps({"error": str(e)}))
      `]);

      pythonProcess.stdin.write(transcript);
      pythonProcess.stdin.end();

      let outputData = '';
      pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        console.error("Python Error: " + data.toString());
      });

      pythonProcess.on('close', (code) => {
        try {
          const result = JSON.parse(outputData);
          if (result.error) {
            console.error("Python script error:", result.error);
            resolve(NextResponse.json({ error: "Backend processing failed" }, { status: 500 }));
          } else {
            resolve(NextResponse.json(result));
          }
        } catch (e) {
          console.error("Parse error from Python:", e);
          resolve(NextResponse.json({ error: "Failed to parse Python output" }, { status: 500 }));
        }
      });
    });
  } catch (error) {
    console.error("API Server error:", error);
    return NextResponse.json({ error: "Server error" }, { status: 500 });
  }
}