import fs from 'node:fs';
export function readAccess(path='.deploy/public-access.json') {
  try { const value=JSON.parse(fs.readFileSync(path,'utf8')); return value.enabled===true; }
  catch { return false; } // Fail closed for missing or malformed state.
}
if (process.argv[1] && import.meta.url===new URL(process.argv[1],'file:').href) {
  console.log(readAccess()?'true':'false');
}
