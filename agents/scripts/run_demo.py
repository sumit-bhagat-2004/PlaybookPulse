"""Demo runner script"""
import asyncio
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.orchestrator import OrchestratorAgent
from app.utils.logger import setup_logging, logger


async def run_demo():
    """Run a demo analysis with sample data"""
    
    setup_logging()
    logger.info("Starting demo analysis...")
    
    # Load sample playbook
    playbook_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'app',
        'data',
        'fixtures',
        'playbook_sample.md'
    )
    
    with open(playbook_path, 'r') as f:
        playbook_content = f.read()
    
    # Create orchestrator
    orchestrator = OrchestratorAgent()
    
    # Run analysis
    input_data = {
        "playbook_content": playbook_content,
        "slack_thread_id": None,  # Would need real IDs for integrations
        "jira_ticket_id": None,
        "github_repo": None,
        "compliance_frameworks": ["nist_sp_800_61"]
    }
    
    logger.info("Running analysis...")
    result = await orchestrator.process(input_data)
    
    if result["success"]:
        logger.info("Analysis completed successfully!")
        logger.info(f"Analysis ID: {result['data']['analysis_id']}")
        logger.info(f"Status: {result['data']['status']}")
        logger.info(f"Steps parsed: {len(result['data']['playbook_steps'])}")
        logger.info(f"Overall score: {result['data']['overall_score']}%")
        
        # Save result
        output_path = "demo_analysis_result.json"
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"Results saved to: {output_path}")
    else:
        logger.error(f"Analysis failed: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(run_demo())
