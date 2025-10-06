"""
CLI entrypoint for the recs services.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add the app directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def ingest_command(args):
    """Handle ingest command."""
    from recs.services.ingest import IngestService

    # Initialize ingest service
    ingest_service = IngestService()

    # Handle different commands
    if args.stats:
        # Show catalog statistics
        stats = ingest_service.get_catalog_stats()
        if stats.get('exists'):
            print(f"📊 Catalog Statistics:")
            print(f"   File: {ingest_service.catalog_path}")
            print(f"   Size: {stats['file_size_mb']} MB ({stats['file_size_bytes']} bytes)")
            print(f"   Items: {stats['line_count']}")
        else:
            print("❌ No catalog file found")
            return 1

    elif args.manifest:
        # Show manifest information
        manifest = ingest_service.get_manifest()
        if manifest:
            print(f"📋 Manifest Information:")
            print(f"   Fetched at: {manifest['fetched_at']}")
            print(f"   Count: {manifest['count']}")
            print(f"   Total processed: {manifest['total_processed']}")
            print(f"   Errors: {manifest['errors']}")
            print(f"   Source: {manifest['source_file']}")
            print(f"   Output: {manifest['output_file']}")
        else:
            print("❌ No manifest file found")
            return 1

    else:
        # Run ingestion
        logger = logging.getLogger(__name__)
        logger.info("Starting ingestion process...")

        if args.source:
            logger.info(f"Using source file: {args.source}")
        else:
            logger.info("Using configured source file")

        # Run the ingestion
        manifest = ingest_service.normalize_and_write(args.source)

        # Print results
        print(f"✅ Ingestion completed successfully!")
        print(f"   Items processed: {manifest['total_processed']}")
        print(f"   Items written: {manifest['count']}")
        print(f"   Errors: {manifest['errors']}")
        print(f"   Output: {manifest['output_file']}")
        print(f"   Manifest: {ingest_service.manifest_path}")

        if manifest['count'] == 0:
            print("⚠️  Warning: No items were written to the catalog")
            return 1

    return 0

def embed_command(args):
    """Handle embed command."""
    from recs.services.embed_openai import EmbedOpenAIService

    # Initialize embeddings service
    embed_service = EmbedOpenAIService()

    # Handle different commands
    if args.stats:
        # Show index statistics
        stats = embed_service.get_index_stats()
        print(f"📊 Index Statistics:")
        print(f"   Embeddings file exists: {'✅' if stats.get('embeddings_exists') else '❌'}")
        print(f"   FAISS index exists: {'✅' if stats.get('faiss_index_exists') else '❌'}")
        print(f"   ID map exists: {'✅' if stats.get('id_map_exists') else '❌'}")
        print(f"   Metadata exists: {'✅' if stats.get('meta_exists') else '❌'}")

        if stats.get('embeddings_shape'):
            print(f"   Embeddings shape: {stats['embeddings_shape']}")
            print(f"   Embeddings size: {stats.get('embeddings_size_mb', 0)} MB")

        if stats.get('faiss_vectors'):
            print(f"   FAISS vectors: {stats['faiss_vectors']}")
            print(f"   FAISS dimension: {stats.get('faiss_dimension', 0)}")

        if stats.get('id_map_count'):
            print(f"   ID map count: {stats['id_map_count']}")

        if stats.get('meta_count'):
            print(f"   Metadata count: {stats['meta_count']}")

        if stats.get('faiss_error'):
            print(f"   FAISS error: {stats['faiss_error']}")

    elif args.search:
        # Search for similar items
        logger = logging.getLogger(__name__)
        logger.info(f"Searching for items similar to: {args.search}")

        # Create embedding for the search query
        query_text = embed_service.prepare_text_for_embedding({'title': args.search})
        logger.info(f"Query text: {query_text}")

        # Create embedding
        query_embedding = embed_service.create_embeddings_batch([query_text])[0]

        # Search for similar items
        results = embed_service.search_similar(query_embedding, k=args.k)

        if results:
            print(f"🔍 Search Results for '{args.search}':")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title']} (ID: {result['id']})")
                print(f"      Score: {result['score']:.4f}")
                print(f"      Brand: {result['metadata'].get('brand', 'N/A')}")
                print(f"      Category: {result['metadata'].get('category', {}).get('level_1', 'N/A')}")
                print(f"      Style: {result['metadata'].get('style', 'N/A')}")
                print()
        else:
            print("❌ No similar items found")
            return 1

    else:
        # Run embeddings processing
        logger = logging.getLogger(__name__)
        logger.info("Starting embeddings processing...")

        if not Path(args.catalog).exists():
            logger.error(f"Catalog file not found: {args.catalog}")
            return 1

        logger.info(f"Using catalog file: {args.catalog}")

        # Run the embeddings processing
        result = embed_service.process_embeddings(args.catalog)

        # Print results
        print(f"✅ Embeddings processing completed!")
        print(f"   Total items: {result['total_items']}")
        print(f"   Processed: {result['processed']}")
        print(f"   Errors: {result['errors']}")
        print(f"   Embeddings: {result['embeddings_file']}")
        print(f"   FAISS index: {result['faiss_index']}")
        print(f"   ID map: {result['id_map']}")
        print(f"   Metadata: {result['meta']}")

        if result['processed'] == 0:
            print("⚠️  Warning: No items were processed")
            return 1

    return 0

def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description='Recommendations system services'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest and normalize product data')
    ingest_parser.add_argument('--source', type=str, help='Path to source data file (JSON/JSONL)')
    ingest_parser.add_argument('--stats', action='store_true', help='Show catalog statistics')
    ingest_parser.add_argument('--manifest', action='store_true', help='Show manifest information')

    # Embed command
    embed_parser = subparsers.add_parser('embed', help='Generate embeddings and build FAISS index')
    embed_parser.add_argument('--catalog', type=str, default='/app/data/catalog.jsonl',
                             help='Path to catalog.jsonl file')
    embed_parser.add_argument('--stats', action='store_true', help='Show index statistics')
    embed_parser.add_argument('--search', type=str, help='Search for similar items using a text query')
    embed_parser.add_argument('--k', type=int, default=10, help='Number of similar items to return')

    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Setup logging
    setup_logging(args.verbose)

    try:
        if args.command == 'ingest':
            return ingest_command(args)
        elif args.command == 'embed':
            return embed_command(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Command failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
