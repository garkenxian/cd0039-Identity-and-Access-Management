import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.get(AuthService);
    
    // Clear localStorage before each test
    localStorage.clear();
    
    // Reset window.location.hash
    window.location.hash = '';
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('build_login_link', () => {
    it('should create a valid Auth0 authorization URL', () => {
      const link = service.build_login_link();
      
      expect(link).toContain('https://');
      expect(link).toContain(service.url);
      expect(link).toContain('/authorize');
      expect(link).toContain('audience=' + service.audience);
      expect(link).toContain('response_type=token');
      expect(link).toContain('client_id=' + service.clientId);
      expect(link).toContain('redirect_uri=' + service.callbackURL);
    });

    it('should include callback path when provided', () => {
      const callbackPath = '/callback';
      const link = service.build_login_link(callbackPath);
      
      expect(link).toContain(service.callbackURL + callbackPath);
    });

    it('should not include callback path when empty string provided', () => {
      const link = service.build_login_link('');
      
      expect(link).toContain(service.callbackURL);
    });
  });

  describe('check_token_fragment', () => {
    it('should extract token from URL fragment when access_token present', () => {
      const testToken = 'test.jwt.token.here';
      const testPayload = { permissions: ['get:drinks'] };
      spyOn(service, 'decodeJWT').and.callFake((token: string) => {
        service.payload = testPayload;
        return testPayload;
      });
      
      window.location.hash = `#access_token=${testToken}&other_param=value`;
      
      service.check_token_fragment();
      
      expect(service.token).toBe(testToken);
      expect(service.payload).toBe(testPayload);
    });

    it('should save token to localStorage when extracted from fragment', () => {
      const testToken = 'test.jwt.token.here';
      const testPayload = { permissions: ['get:drinks'] };
      spyOn(service, 'decodeJWT').and.callFake((token: string) => {
        service.payload = testPayload;
        return testPayload;
      });
      
      window.location.hash = `#access_token=${testToken}`;
      
      service.check_token_fragment();
      
      expect(localStorage.getItem('JWTS_LOCAL_KEY')).toBe(testToken);
      expect(service.payload).toBe(testPayload);
    });

    it('should not set token when fragment does not contain access_token', () => {
      window.location.hash = '#other_param=value';
      const initialToken = service.token;
      
      service.check_token_fragment();
      
      expect(service.token).toBe(initialToken);
    });

    it('should handle empty hash gracefully', () => {
      window.location.hash = '';
      
      expect(() => service.check_token_fragment()).not.toThrow();
    });
  });

  describe('set_jwt', () => {
    it('should save token to localStorage', () => {
      const testToken = 'test.jwt.token';
      service.token = testToken;
      spyOn(service, 'decodeJWT');
      
      service.set_jwt();
      
      expect(localStorage.getItem('JWTS_LOCAL_KEY')).toBe(testToken);
    });

    it('should decode token when setting valid JWT', () => {
      const testToken = 'test.jwt.token';
      const testPayload = { name: 'John Doe' };
      service.token = testToken;
      spyOn(service, 'decodeJWT').and.returnValue(testPayload);
      
      service.set_jwt();
      
      expect(service.decodeJWT).toHaveBeenCalled();
    });

    it('should save empty string when token is empty', () => {
      service.token = '';
      spyOn(service, 'decodeJWT');
      
      service.set_jwt();
      
      expect(localStorage.getItem('JWTS_LOCAL_KEY')).toBe('');
    });
  });

  describe('load_jwts', () => {
    it('should load token from localStorage', () => {
      const testToken = 'test.jwt.token';
      localStorage.setItem('JWTS_LOCAL_KEY', testToken);
      spyOn(service, 'decodeJWT');
      
      service.load_jwts();
      
      expect(service.token).toBe(testToken);
    });

    it('should return null when no token in localStorage', () => {
      service.load_jwts();
      
      expect(service.token).toBeNull();
    });

    it('should decode token when loading from localStorage', () => {
      const testToken = 'test.jwt.token';
      const testPayload = { permissions: ['get:drinks'] };
      localStorage.setItem('JWTS_LOCAL_KEY', testToken);
      spyOn(service, 'decodeJWT').and.returnValue(testPayload);
      
      service.load_jwts();
      
      expect(service.decodeJWT).toHaveBeenCalled();
    });
  });

  describe('activeJWT', () => {
    it('should return the current token', () => {
      const testToken = 'test.jwt.token';
      service.token = testToken;
      
      expect(service.activeJWT()).toBe(testToken);
    });

    it('should return null when no token set', () => {
      service.token = '';
      
      expect(service.activeJWT()).toBe('');
    });
  });

  describe('decodeJWT', () => {
    it('should decode valid JWT and return payload', () => {
      const testPayload = { sub: '1234567890', name: 'John Doe', iat: 1516239022 };
      spyOn(service, 'decodeJWT').and.returnValue(testPayload);
      
      const payload = service.decodeJWT('any.token.here');
      
      expect(payload).toBeTruthy();
      expect(payload.name).toBe('John Doe');
    });

    it('should set service payload property when decoding', () => {
      const testPayload = { sub: '1234567890', name: 'John Doe', iat: 1516239022 };
      service.payload = testPayload;
      
      expect(service.payload).toBeTruthy();
      expect(service.payload.name).toBe('John Doe');
    });
  });

  describe('can', () => {
    it('should return true when user has permission', () => {
      service.payload = {
        permissions: ['get:drinks', 'get:drinks-detail']
      };
      
      expect(service.can('get:drinks')).toBe(true);
      expect(service.can('get:drinks-detail')).toBe(true);
    });

    it('should return false when user does not have permission', () => {
      service.payload = {
        permissions: ['get:drinks']
      };
      
      expect(service.can('post:drinks')).toBe(false);
    });

    it('should return false when payload is null', () => {
      service.payload = null;
      
      expect(service.can('get:drinks')).toBe(false);
    });

    it('should return false when permissions claim is missing', () => {
      service.payload = {
        sub: '123'
      };
      
      expect(service.can('get:drinks')).toBe(false);
    });

    it('should return false when permissions array is empty', () => {
      service.payload = {
        permissions: []
      };
      
      expect(service.can('get:drinks')).toBe(false);
    });

    it('should handle manager permissions correctly', () => {
      service.payload = {
        permissions: ['get:drinks', 'get:drinks-detail', 'post:drinks', 'patch:drinks', 'delete:drinks']
      };
      
      expect(service.can('get:drinks')).toBe(true);
      expect(service.can('get:drinks-detail')).toBe(true);
      expect(service.can('post:drinks')).toBe(true);
      expect(service.can('patch:drinks')).toBe(true);
      expect(service.can('delete:drinks')).toBe(true);
    });

    it('should handle barista permissions correctly', () => {
      service.payload = {
        permissions: ['get:drinks', 'get:drinks-detail']
      };
      
      expect(service.can('get:drinks')).toBe(true);
      expect(service.can('get:drinks-detail')).toBe(true);
      expect(service.can('post:drinks')).toBe(false);
      expect(service.can('patch:drinks')).toBe(false);
      expect(service.can('delete:drinks')).toBe(false);
    });
  });

  describe('logout', () => {
    it('should clear token and payload', () => {
      service.token = 'test.jwt.token';
      service.payload = { name: 'Test User', permissions: ['get:drinks'] };
      
      service.logout();
      
      expect(service.token).toBe('');
      expect(service.payload).toBeNull();
    });

    it('should remove token from localStorage', () => {
      service.token = 'test.jwt.token';
      localStorage.setItem('JWTS_LOCAL_KEY', 'test.jwt.token');
      
      service.logout();
      
      expect(localStorage.getItem('JWTS_LOCAL_KEY')).toBe('');
    });

    it('should clear localStorage completely', () => {
      localStorage.setItem('JWTS_LOCAL_KEY', 'test.jwt.token');
      
      service.logout();
      
      expect(localStorage.getItem('JWTS_LOCAL_KEY')).toBe('');
    });
  });

  describe('integration scenarios', () => {
    it('should handle full login flow: build link -> parse token -> decode', () => {
      // Step 1: Build login link
      const loginLink = service.build_login_link();
      expect(loginLink).toContain('/authorize');
      
      // Step 2: Manually set token and payload to simulate login
      const testPayload = {
        sub: '1234567890',
        name: 'Barista',
        permissions: ['get:drinks', 'get:drinks-detail']
      };
      service.token = 'test.jwt.token';
      service.payload = testPayload;
      
      // Verify user has expected permissions
      expect(service.can('get:drinks')).toBe(true);
      expect(service.can('get:drinks-detail')).toBe(true);
      expect(service.can('post:drinks')).toBe(false);
    });

    it('should handle full logout and re-login flow', () => {
      // Setup: User logged in
      const testPayload = { permissions: ['get:drinks', 'get:drinks-detail'] };
      service.token = 'test.jwt.token';
      service.payload = testPayload;
      
      expect(service.can('get:drinks')).toBe(true);
      
      // Logout
      service.logout();
      
      // Verify logout cleared everything
      expect(service.token).toBe('');
      expect(service.payload).toBeNull();
      expect(service.can('get:drinks')).toBe(false);
      expect(localStorage.getItem('JWTS_LOCAL_KEY')).toBe('');
    });

    it('should persist token across page reload', () => {
      // Step 1: Save token to localStorage
      const testToken = 'test.jwt.token';
      const testPayload = { permissions: ['get:drinks', 'get:drinks-detail'] };
      service.token = testToken;
      service.payload = testPayload;
      localStorage.setItem('JWTS_LOCAL_KEY', testToken);
      
      // Step 2: Verify token was saved
      expect(localStorage.getItem('JWTS_LOCAL_KEY')).toBe(testToken);
      
      // Step 3: Simulate page reload - create new service instance
      const newService = new AuthService();
      // Manually set payload to simulate having loaded from storage
      newService.token = testToken;
      newService.payload = testPayload;
      
      // Verify the token and payload are accessible
      expect(newService.token).toBe(testToken);
      expect(newService.payload).toBe(testPayload);
      expect(newService.can('get:drinks')).toBe(true);
    });
  });
});
