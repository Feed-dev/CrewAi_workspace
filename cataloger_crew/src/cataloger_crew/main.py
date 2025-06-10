"""
Main entry point for the Cataloger Crew.
Configure and run autonomous web cataloging operations.
"""

import os
import sys
import time
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from cataloger_crew.crew import create_cataloger_crew


def load_environment():
    """Load environment variables from .env file if it exists."""
    env_file = Path(__file__).parent.parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"\'')


def run_cataloger_session(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single cataloging session.
    
    Args:
        config: Configuration dictionary with cataloging parameters
    
    Returns:
        Session results and statistics
    """
    print(f"\n{'='*60}")
    print(f"Starting Cataloger Session: {datetime.now().isoformat()}")
    print(f"Topic: {config['topic']}")
    print(f"Search Terms: {config['search_terms']}")
    print(f"{'='*60}\n")
    
    try:
        # Create and configure crew
        crew = create_cataloger_crew(
            topic=config['topic'],
            search_terms=config['search_terms'],
            search_rounds=config.get('search_rounds', 3),
            search_model=config.get('search_model'),
            analysis_model=config.get('analysis_model'),
            cataloger_model=config.get('cataloger_model')
        )
        
        # Prepare inputs for the crew
        inputs = {
            'topic': config['topic'],
            'search_terms': config['search_terms'],
            'search_rounds': config.get('search_rounds', 3)
        }
        
        # Run the crew
        start_time = time.time()
        result = crew.crew().kickoff(inputs=inputs)
        end_time = time.time()
        
        # Session statistics
        session_stats = {
            'session_start': datetime.now().isoformat(),
            'duration_minutes': (end_time - start_time) / 60,
            'topic': config['topic'],
            'search_rounds': config.get('search_rounds', 3),
            'success': True,
            'result_summary': str(result)[:500] + "..." if len(str(result)) > 500 else str(result)
        }
        
        print(f"\n{'='*60}")
        print(f"Session Completed Successfully!")
        print(f"Duration: {session_stats['duration_minutes']:.2f} minutes")
        print(f"{'='*60}\n")
        
        return session_stats
        
    except Exception as e:
        print(f"\nError in cataloger session: {str(e)}")
        return {
            'session_start': datetime.now().isoformat(),
            'success': False,
            'error': str(e),
            'topic': config['topic']
        }


def run_autonomous_cataloger(config: Dict[str, Any]):
    """
    Run the cataloger in autonomous mode with scheduled sessions.
    
    Args:
        config: Configuration dictionary with cataloging and scheduling parameters
    """
    print(f"\n{'='*80}")
    print(f"AUTONOMOUS CATALOGER CREW STARTING")
    print(f"{'='*80}")
    print(f"Topic: {config['topic']}")
    print(f"Duration: {config.get('duration_hours', 24)} hours")
    print(f"Session Interval: {config.get('session_interval_hours', 4)} hours")
    print(f"Models: Search={config.get('search_model', 'default')}, "
          f"Analysis={config.get('analysis_model', 'default')}, "
          f"Cataloger={config.get('cataloger_model', 'default')}")
    print(f"{'='*80}\n")
    
    # Calculate end time
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=config.get('duration_hours', 24))
    
    session_count = 0
    session_history = []
    
    # Schedule function for sessions
    def scheduled_session():
        nonlocal session_count, session_history
        session_count += 1
        
        print(f"\n🤖 Starting Scheduled Session #{session_count}")
        print(f"⏰ Current Time: {datetime.now().isoformat()}")
        
        # Run the session
        session_result = run_cataloger_session(config)
        session_history.append(session_result)
        
        # Print session summary
        if session_result['success']:
            print(f"✅ Session #{session_count} completed successfully")
        else:
            print(f"❌ Session #{session_count} failed: {session_result.get('error', 'Unknown error')}")
        
        # Check if we should continue
        if datetime.now() >= end_time:
            print(f"\n🏁 Autonomous cataloging duration completed")
            print(f"📊 Total Sessions: {session_count}")
            print(f"✅ Successful: {sum(1 for s in session_history if s['success'])}")
            print(f"❌ Failed: {sum(1 for s in session_history if not s['success'])}")
            return schedule.CancelJob
    
    # Schedule the sessions
    interval_hours = config.get('session_interval_hours', 4)
    schedule.every(interval_hours).hours.do(scheduled_session)
    
    # Run first session immediately
    print("🚀 Running initial session...")
    scheduled_session()
    
    # Main loop
    print(f"\n⏰ Next session scheduled in {interval_hours} hours")
    print(f"🛑 Autonomous operation will end at: {end_time.isoformat()}")
    print(f"💡 Press Ctrl+C to stop early\n")
    
    try:
        while datetime.now() < end_time:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Autonomous cataloging stopped by user")
        print(f"📊 Sessions completed: {session_count}")
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"AUTONOMOUS CATALOGING COMPLETED")
    print(f"{'='*80}")
    print(f"Start Time: {start_time.isoformat()}")
    print(f"End Time: {datetime.now().isoformat()}")
    print(f"Total Sessions: {session_count}")
    
    if session_history:
        successful_sessions = [s for s in session_history if s['success']]
        print(f"Successful Sessions: {len(successful_sessions)}")
        if successful_sessions:
            avg_duration = sum(s.get('duration_minutes', 0) for s in successful_sessions) / len(successful_sessions)
            print(f"Average Session Duration: {avg_duration:.2f} minutes")
    
    print(f"{'='*80}\n")


def main():
    """Main function with example configurations."""
    # Load environment variables
    load_environment()
    
    # Check for required API keys
    if not os.getenv('SERPER_API_KEY'):
        print("⚠️  Warning: SERPER_API_KEY not found in environment variables")
        print("   Set SERPER_API_KEY for web search functionality")
        print("   Get your API key from: https://serper.dev\n")
    
    # Example configurations - modify these for your use case
    
    # Single session configuration
    single_session_config = {
        'topic': 'artificial intelligence machine learning',
        'search_terms': 'AI ML artificial intelligence machine learning deep learning neural networks',
        'search_rounds': 3,
        'search_model': 'llama3.1:8b',
        'analysis_model': 'llama3.1:8b',
        'cataloger_model': 'llama3.1:8b'
    }
    
    # Autonomous operation configuration
    autonomous_config = {
        'topic': 'artificial intelligence machine learning',
        'search_terms': 'AI ML artificial intelligence machine learning deep learning neural networks',
        'search_rounds': 2,  # Fewer rounds for autonomous mode
        'duration_hours': 12,  # Run for 12 hours
        'session_interval_hours': 3,  # New session every 3 hours
        'search_model': 'llama3.1:8b',
        'analysis_model': 'llama3.1:8b',
        'cataloger_model': 'llama3.1:8b'
    }
    
    # Choose mode based on command line argument or default to single session
    mode = sys.argv[1] if len(sys.argv) > 1 else 'single'
    
    if mode == 'autonomous':
        print("🤖 Starting Autonomous Cataloger Mode")
        run_autonomous_cataloger(autonomous_config)
    else:
        print("🔍 Running Single Cataloger Session")
        result = run_cataloger_session(single_session_config)
        
        if result['success']:
            print("\n✅ Cataloging session completed successfully!")
            print("💾 Check the catalog_data/ directory for results")
        else:
            print(f"\n❌ Cataloging session failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()