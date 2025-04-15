#!/usr/bin/env node

/**
 * CLI interface for the TypeScript API.
 * This script is used by the Python API Manager to call TypeScript API methods.
 */

const fs = require('fs');
const path = require('path');
const { buildApiHandler } = require('./index');

// Parse command line arguments
const args = process.argv.slice(2);
let paramsFile = null;
let isStreaming = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--params' && i + 1 < args.length) {
    paramsFile = args[i + 1];
    i++;
  } else if (args[i] === '--stream') {
    isStreaming = true;
  }
}

if (!paramsFile) {
  console.error('Error: --params argument is required');
  process.exit(1);
}

// Read and parse the parameters file
let params;
try {
  const paramsContent = fs.readFileSync(paramsFile, 'utf8');
  params = JSON.parse(paramsContent);
} catch (error) {
  console.error(`Error reading or parsing parameters file: ${error.message}`);
  process.exit(1);
}

// Extract parameters
const { provider, method, params: methodParams } = params;

if (!provider || !method) {
  console.error('Error: provider and method are required in the parameters file');
  process.exit(1);
}

// Build the API handler for the specified provider
const apiConfig = {
  apiProvider: provider,
  ...methodParams
};

try {
  const apiHandler = buildApiHandler(apiConfig);
  
  // Call the specified method
  switch (method) {
    case 'generateText':
      handleGenerateText(apiHandler, methodParams, isStreaming);
      break;
    case 'getTokenCount':
      handleGetTokenCount(apiHandler, methodParams);
      break;
    case 'getAvailableModels':
      handleGetAvailableModels(apiHandler);
      break;
    default:
      console.error(`Error: Unknown method ${method}`);
      process.exit(1);
  }
} catch (error) {
  console.error(`Error building API handler: ${error.message}`);
  process.exit(1);
}

/**
 * Handle the generateText method.
 * 
 * @param {Object} apiHandler - The API handler instance
 * @param {Object} params - The method parameters
 * @param {boolean} isStreaming - Whether to stream the response
 */
function handleGenerateText(apiHandler, params, isStreaming) {
  const { prompt, systemPrompt, model, temperature, maxTokens, stream } = params;
  
  // Create messages array for the API
  const messages = [
    { role: 'user', content: prompt }
  ];
  
  if (systemPrompt) {
    messages.unshift({ role: 'system', content: systemPrompt });
  }
  
  // Call the API
  const stream = apiHandler.createMessage(systemPrompt || '', messages);
  
  if (isStreaming) {
    // Stream the response
    stream.on('data', (chunk) => {
      console.log(JSON.stringify({ text: chunk.text }));
    });
    
    stream.on('end', () => {
      process.exit(0);
    });
    
    stream.on('error', (error) => {
      console.error(`Error streaming response: ${error.message}`);
      process.exit(1);
    });
  } else {
    // Collect the full response
    let fullText = '';
    
    stream.on('data', (chunk) => {
      fullText += chunk.text;
    });
    
    stream.on('end', () => {
      console.log(JSON.stringify({ text: fullText }));
      process.exit(0);
    });
    
    stream.on('error', (error) => {
      console.error(`Error generating text: ${error.message}`);
      process.exit(1);
    });
  }
}

/**
 * Handle the getTokenCount method.
 * 
 * @param {Object} apiHandler - The API handler instance
 * @param {Object} params - The method parameters
 */
function handleGetTokenCount(apiHandler, params) {
  const { text, model } = params;
  
  // Use the API handler's token counting method if available
  if (typeof apiHandler.getTokenCount === 'function') {
    const count = apiHandler.getTokenCount(text, model);
    console.log(JSON.stringify({ count }));
  } else {
    // Fallback to a simple estimation
    const words = text.split(/\s+/).length;
    const estimatedTokens = Math.ceil(words * 1.3); // Rough estimate
    console.log(JSON.stringify({ count: estimatedTokens }));
  }
  
  process.exit(0);
}

/**
 * Handle the getAvailableModels method.
 * 
 * @param {Object} apiHandler - The API handler instance
 */
function handleGetAvailableModels(apiHandler) {
  // Get the model information from the API handler
  const modelInfo = apiHandler.getModel();
  
  // Return the model information
  console.log(JSON.stringify({ 
    models: [modelInfo]
  }));
  
  process.exit(0);
}
