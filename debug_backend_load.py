import requests, time


# Test script for backend load
def test_backend():
    url = "http://localhost:8000/analyze"
    # Create a dummy VCF file content if one doesn't exist for the test
    vcf_content = b"""##fileformat=VCFv4.2
#CHROM POS ID REF ALT QUAL FILTER INFO
chr10 96526135 . G A . . .
"""

    files = {"vcf": ("test.vcf", vcf_content, "text/plain")}

    # We'll test with the 6 supported drugs
    drugs = [
        "WARFARIN",
        "CLOPIDOGREL",
        "SIMVASTATIN",
        "CODEINE",
        "AZATHIOPRINE",
        "FLUOROURACIL",
    ]
    data = {
        "drugs": ",".join(drugs),  # Comma separated list as string
        "indication": "General Checkup",
    }

    print(f"Sending request for {len(drugs)} drugs...")
    start_time = time.time()

    try:
        # Increase timeout beyond 90s to verify if backend finishes eventualy
        response = requests.post(url, files=files, data=data, timeout=120)

        duration = time.time() - start_time
        print(f"Completed in {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            results = response.json()
            print(f"Received results for {len(results)} drugs")
            for r in results:
                print(
                    f"- {r.get('drug_name', 'Unknown')}: {len(r.get('llm_analysis', ''))} chars"
                )
        else:
            print(f"Error Response: {response.text[:200]}")

    except requests.exceptions.Timeout:
        print(f"Request TIMED OUT after {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f"Request FAILED: {str(e)}")


if __name__ == "__main__":
    test_backend()
