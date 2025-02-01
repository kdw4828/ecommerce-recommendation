import subprocess

def invalidate_cloudfront_cache(distribution_id, paths="/*"):
    command = [
        "aws", "cloudfront", "create-invalidation",
        "--distribution-id", distribution_id,
        "--paths", paths
    ]
    subprocess.run(command)

if __name__ == "__main__":
    invalidate_cloudfront_cache(distribution_id="E3AA2AFV9RFR4J", paths="/*")
