// MongoDB initialization script
// This script runs when MongoDB container starts for the first time

print('Starting MongoDB initialization...');

// Switch to the database
db = db.getSiblingDB('ai-marketing-saas');

// Create collections
print('Creating collections...');

// User collection
db.createCollection('users');
print('Created users collection');

// Generated content collection
db.createCollection('generatedcontents');
print('Created generatedcontents collection');

// Content templates collection
db.createCollection('contenttemplates');
print('Created contenttemplates collection');

// Create indexes for performance
print('Creating indexes...');

// Users collection indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ createdAt: 1 });
print('Created users indexes');

// Generated content indexes
db.generatedcontents.createIndex({ userId: 1, createdAt: -1 });
db.generatedcontents.createIndex({ templateId: 1 });
print('Created generatedcontents indexes');

// Content templates indexes
db.contenttemplates.createIndex({ type: 1 });
db.contenttemplates.createIndex({ category: 1 });
print('Created contenttemplates indexes');

print('MongoDB initialization completed successfully!');



