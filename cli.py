from __future__ import annotations
import json, argparse, os, pathlib
from agents.profiler import talent_intelligence_report
from agents.assessment_designer import generate_assessment
from agents.behavioral import analyze_transcript
from agents.market_intel import load_market, summarize

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate-id', required=True)
    ap.add_argument('--role', default='AI Engineer')
    ap.add_argument('--level', default='Mid', choices=['Junior','Mid','Senior'])
    ap.add_argument('--profiles', default='data/synthetic_profiles.json')
    ap.add_argument('--transcripts', default='data/transcripts.json')
    ap.add_argument('--market', default='data/market_compensation.csv')
    ap.add_argument('--outdir', default='outputs')
    args = ap.parse_args()

    profiles = json.load(open(args.profiles))
    transcripts = json.load(open(args.transcripts))
    market_df = load_market(args.market)

    profile = next((p for p in profiles if p['id']==args.candidate_id), None)
    if not profile:
        raise SystemExit(f"Candidate {args.candidate_id} not found.")

    report = talent_intelligence_report(profile)
    package = generate_assessment(report, role=args.role, level=args.level)
    behavior = analyze_transcript(transcripts.get(args.candidate_id, []))
    market = summarize(market_df, role=args.role, region='Bangalore', level=args.level)

    os.makedirs(args.outdir, exist_ok=True)
    base = pathlib.Path(args.outdir)/f"{args.candidate_id}_{args.role.replace(' ','_')}_{args.level}"
    with open(str(base)+"_report.json", 'w') as f: json.dump(report, f, indent=2)
    with open(str(base)+"_assessment.json", 'w') as f: json.dump(package, f, indent=2)
    with open(str(base)+"_behavior.json", 'w') as f: json.dump(behavior, f, indent=2)
    with open(str(base)+"_market.json", 'w') as f: json.dump(market, f, indent=2)

    print("Written outputs to:", args.outdir)

if __name__ == '__main__':
    main()
