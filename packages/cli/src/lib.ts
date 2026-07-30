/**
 * Public library entry point for @apex-pred/cli.
 *
 * Importing this module does not start the CLI — `dist/index.js` is the
 * executable entry (see the `apex` bin), this is the programmatic one.
 */
export { ApexPredAgent } from './agent.js';
export { getConfig, setConfig, getConfigPath, type ApexConfig } from './config.js';
export { SessionManager, type Session } from './session.js';
export { startInteractive, runOneShot } from './cli.js';
export {
  APEX_PRED_SYSTEM_PROMPT,
  APEX_PRED_BANNER,
  WELCOME_MESSAGE,
} from './personality.js';
export {
  createToolRegistry,
  getToolSpecs,
  type ToolRegistry,
  type ToolResult,
} from './tools/index.js';
export { theme } from './ui/theme.js';
