#!/usr/bin/env python3
"""
Migration script to transition from current memory structure to enhanced organized structure
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict

from modules.agents.enhanced_memory_manager import EnhancedMemoryManager
from modules.agents.memory_manager import MemoryManager
from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


class MemoryMigrator:
    """Migrates existing memory structure to enhanced organized structure"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        #Initialize managers
        self.config_manager = ConfigManager()
        self.llm_manager = LLMManager(self.config_manager)
        self.old_memory = MemoryManager(self.llm_manager, self.config_manager)
        self.new_memory = EnhancedMemoryManager(self.llm_manager, self.config_manager)

        #Migration mapping
        self.collection_mapping = {
            "user_feedback": "user_feedback",  #Keep the same
            "successful_plans": "master_agent_plans",  #Move to agent-specific
            #Add more mappings as needed
        }

    def analyze_current_structure(self) -> Dict[str, Any]:
        """Analyze current memory structure"""
        try:
            collections = self.old_memory.client.list_collections()
            analysis = {
                "total_collections": len(collections),
                "collections": {},
                "total_memories": 0,
                "unorganized_memories": 0,
            }

            for coll in collections:
                collection = self.old_memory.client.get_collection(
                    name=coll.name,
                    embedding_function=self.old_memory._get_embedding_function(),
                )
                count = collection.count()
                analysis["total_memories"] += count
                analysis["collections"][coll.name] = {
                    "count": count,
                    "organized": coll.name in self.collection_mapping,
                }

                if coll.name not in self.collection_mapping:
                    analysis["unorganized_memories"] += count

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing current structure: {e}")
            return {}

    def migrate_collection(self, old_name: str, new_name: str) -> int:
        """Migrate a single collection to new structure"""
        try:
            #Get old collection
            old_collection = self.old_memory.client.get_collection(
                name=old_name,
                embedding_function=self.old_memory._get_embedding_function(),
            )

            #Get all data from old collection
            all_data = old_collection.get(include=["documents", "metadatas", "embeddings"])

            if not all_data["ids"]:
                self.logger.info(f"Collection '{old_name}' is empty, skipping migration")
                return 0

            #Add to new collection with enhanced metadata
            migrated_count = 0

            for i, doc_id in enumerate(all_data["ids"]):
                content = all_data["documents"][i]
                old_metadata = all_data["metadatas"][i] if all_data["metadatas"] else {}

                #Enhance metadata for new structure
                new_metadata = old_metadata.copy()
                new_metadata.update({
                    "migrated_from": old_name,
                    "migration_timestamp": time.time(),
                    "original_id": doc_id,
                })

                #Add to new collection
                self.new_memory.add_memory(content, new_name, new_metadata)
                migrated_count += 1

            self.logger.info(f"Migrated {migrated_count} memories from '{old_name}' to '{new_name}'")
            return migrated_count

        except Exception as e:
            self.logger.error(f"Error migrating collection '{old_name}': {e}")
            return 0

    def migrate_all(self, backup_old: bool = True) -> Dict[str, Any]:
        """Migrate all collections to new structure"""
        start_time = time.time()
        migration_results = {
            "total_migrated": 0,
            "collections_migrated": {},
            "errors": [],
            "backup_created": False,
        }

        try:
            #Analyze current structure
            analysis = self.analyze_current_structure()
            self.logger.info(f"Starting migration of {analysis['total_memories']} memories from {analysis['total_collections']} collections")

            #Create backup if requested
            if backup_old:
                backup_path = self._create_backup()
                migration_results["backup_created"] = backup_path is not None
                migration_results["backup_path"] = backup_path

            #Migrate known collections
            for old_name, new_name in self.collection_mapping.items():
                try:
                    migrated = self.migrate_collection(old_name, new_name)
                    migration_results["collections_migrated"][old_name] = {
                        "new_name": new_name,
                        "migrated_count": migrated,
                    }
                    migration_results["total_migrated"] += migrated
                except Exception as e:
                    error_msg = f"Failed to migrate '{old_name}': {e}"
                    migration_results["errors"].append(error_msg)
                    self.logger.error(error_msg)

            #Handle unmapped collections
            collections = self.old_memory.client.list_collections()
            for coll in collections:
                if coll.name not in self.collection_mapping:
                    #Try to auto-categorize
                    new_name = self._auto_categorize_collection(coll.name)
                    if new_name:
                        try:
                            migrated = self.migrate_collection(coll.name, new_name)
                            migration_results["collections_migrated"][coll.name] = {
                                "new_name": new_name,
                                "migrated_count": migrated,
                                "auto_categorized": True,
                            }
                            migration_results["total_migrated"] += migrated
                        except Exception as e:
                            error_msg = f"Failed to auto-migrate '{coll.name}': {e}"
                            migration_results["errors"].append(error_msg)
                            self.logger.error(error_msg)

            duration = time.time() - start_time
            self.logger.info(f"Migration completed in {duration:.2f} seconds. Migrated {migration_results['total_migrated']} memories.")

            return migration_results

        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            migration_results["errors"].append(f"Migration failed: {e}")
            return migration_results

    def _auto_categorize_collection(self, collection_name: str) -> str:
        """Auto-categorize unknown collections"""
        name_lower = collection_name.lower()

        #Agent-specific patterns
        if "master" in name_lower or "plan" in name_lower:
            return "master_agent_plans"
        if "screen" in name_lower:
            return "screen_agent_observations"
        if "browser" in name_lower:
            return "browser_agent_interactions"
        if "security" in name_lower:
            return "security_agent_events"
        if "deputy" in name_lower:
            return "deputy_agent_monitoring"

        #Data type patterns
        if "feedback" in name_lower:
            return "user_feedback"
        if "preference" in name_lower:
            return "user_preferences"
        if "session" in name_lower:
            return "current_session"
        if "error" in name_lower:
            return "error_solutions"
        if "success" in name_lower:
            return "successful_patterns"

        #Default to system knowledge
        return "system_knowledge"

    def _create_backup(self) -> str:
        """Create backup of current memory structure"""
        try:
            backup_dir = Path(self.config_manager.get_app_data_path("memory_backup"))
            backup_dir.mkdir(exist_ok=True)

            timestamp = int(time.time())
            backup_path = backup_dir / f"memory_backup_{timestamp}"

            #Copy current database
            import shutil
            current_db_path = self.config_manager.get_app_data_path("memory")
            shutil.copytree(current_db_path, backup_path)

            self.logger.info(f"Backup created at: {backup_path}")
            return str(backup_path)

        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None


def main():
    """Run migration"""
    logging.basicConfig(level=logging.INFO)

    migrator = MemoryMigrator()

    print("🧠 Atlas Memory Migration Tool")
    print("=" * 40)

    #Analyze current structure
    analysis = migrator.analyze_current_structure()
    print("Current memory structure:")
    print(f"  Total collections: {analysis['total_collections']}")
    print(f"  Total memories: {analysis['total_memories']}")
    print(f"  Unorganized memories: {analysis['unorganized_memories']}")
    print()

    for name, info in analysis["collections"].items():
        status = "✅ Organized" if info["organized"] else "⚠️  Unorganized"
        print(f"  {name}: {info['count']} memories - {status}")

    print()

    #Ask for confirmation
    response = input("Proceed with migration? (y/N): ").strip().lower()
    if response != "y":
        print("Migration cancelled.")
        return

    #Run migration
    print("\n🚀 Starting migration...")
    results = migrator.migrate_all(backup_old=True)

    print("\n📊 Migration Results:")
    print(f"  Total migrated: {results['total_migrated']} memories")
    print(f"  Backup created: {'✅' if results['backup_created'] else '❌'}")

    if "backup_path" in results:
        print(f"  Backup location: {results['backup_path']}")

    print("  Collections migrated:")
    for old_name, info in results["collections_migrated"].items():
        auto_note = " (auto-categorized)" if info.get("auto_categorized") else ""
        print(f"    {old_name} → {info['new_name']}: {info['migrated_count']} memories{auto_note}")

    if results["errors"]:
        print(f"  Errors ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"    ❌ {error}")

    print("\n✅ Migration completed!")
    print("\nNext steps:")
    print("1. Test the new memory structure")
    print("2. Update agents to use EnhancedMemoryManager")
    print("3. Remove old collections after verification")


if __name__ == "__main__":
    main()
