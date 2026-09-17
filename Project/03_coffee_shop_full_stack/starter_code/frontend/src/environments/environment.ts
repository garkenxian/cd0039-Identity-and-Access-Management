/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-53bey634viqgnyzc.us.auth0.com', // Auth0 domain from tenant setup
    audience: 'coffee-shop-api', // Must match API_AUDIENCE in backend auth.py
    clientId: 'LhgYzneJPGKmuasdbBAQaMQt6MCEwYar', // Auth0 SPA application Client ID
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};

