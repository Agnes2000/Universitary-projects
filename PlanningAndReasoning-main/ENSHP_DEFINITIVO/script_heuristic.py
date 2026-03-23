import subprocess
import csv

heuristics = ["hadd", "hmax", "hradd", "hrmax"]
strategies = ["gbfs", "WAStar", "wa_star_4"]
results = []

for h in heuristics:
    for s in strategies:
        print(f"Running heuristic: {h}, strategy: {s}")

        cmd = [
            "java", "-jar", "enhsp-20.jar",
            "-o", "domain.pddl",
            "-f", "instance3.pddl",
            "-h", h,
            "-s", s
        ]

        try:
            output = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(f"Error running ENHSP with heuristic {h} and strategy {s}")
            results.append([h, s, -1, -1, -1, -1])
            continue

        states = -1
        time = -1
        plan_length = -1
        metric = -1

        for line in output.splitlines():
            line = line.strip()
            if line.startswith("States Evaluated:"):
                states = int(line.split(":")[1].strip())
            elif line.startswith("Search Time (msec):"):
                time = int(line.split(":")[1].strip())
            elif line.startswith("Plan-Length:"):
                plan_length = int(line.split(":")[1].strip())
            elif line.startswith("Metric (Search):"):
                metric = float(line.split(":")[1].strip())

        results.append([h, s, states, time, plan_length, metric])

print("Dati raccolti:", results)

# Salva su CSV
with open("enhsp_results.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["heuristic", "strategy", "states", "time", "plan_length", "metric"])
    writer.writerows(results)

print("Dati salvati in 'enhsp_results.csv'")
