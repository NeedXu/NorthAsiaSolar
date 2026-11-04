import fs from 'node:fs';
// Called only in a GitHub Actions runner. Never ship this token to the frontend.
export async function changePages({action, repository, token, request=fetch}) {
  if(!['close','open'].includes(action))throw Error('Unsupported access action');
  if(!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repository||'')||!token)throw Error('Missing runner authorization');
  const url=`https://api.github.com/repos/${repository}/pages`;
  const options={headers:{Authorization:`Bearer ${token}`,Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'}};
  if(action==='close'){
    const response=await request(url,{...options,method:'DELETE'});
    // A 404 can indicate lack of permission: never claim successful shutdown from it.
    if(response.status!==204)throw Error(`Pages shutdown not confirmed (HTTP ${response.status}). Keep deployment disabled; repository owner must use Settings > Pages > Unpublish site.`);
    return 'Pages site deleted. Deployment remains disabled.';
  }
  const response=await request(url,{...options,method:'GET'});
  if(response.status===200){const site=await response.json();if(site.build_type!=='workflow')throw Error('Set Pages source to GitHub Actions before opening.');return 'Pages configured for workflow deployment.';}
  if(response.status!==404)throw Error(`Pages status check failed (HTTP ${response.status}).`);
  const created=await request(url,{...options,method:'POST',body:JSON.stringify({build_type:'workflow'})});
  if(created.status!==201)throw Error(`Pages creation failed (HTTP ${created.status}). Repository owner must enable Pages using GitHub Actions.`);
  return 'Pages created for workflow deployment.';
}
if(process.argv[1]&&import.meta.url===new URL(process.argv[1],'file:').href){
  changePages({action:process.env.ACCESS_ACTION,repository:process.env.GITHUB_REPOSITORY,token:process.env.GITHUB_TOKEN})
    .then(message=>{fs.writeFileSync('.deploy/access-result.json',JSON.stringify({action:process.env.ACCESS_ACTION,status:'ok',message,at:new Date().toISOString()})+'\n');console.log(message)}).catch(error=>{fs.writeFileSync('.deploy/access-result.json',JSON.stringify({action:process.env.ACCESS_ACTION,status:'error',message:error.message,at:new Date().toISOString()})+'\n');console.error('::error::'+error.message);process.exitCode=1});
}
