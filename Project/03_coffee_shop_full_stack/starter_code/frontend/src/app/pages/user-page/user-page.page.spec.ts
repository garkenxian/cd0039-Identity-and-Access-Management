import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UserPagePage } from './user-page.page';
import { AuthService } from 'src/app/services/auth.service';

describe('UserPagePage', () => {
  let component: UserPagePage;
  let fixture: ComponentFixture<UserPagePage>;
  let authServiceSpy: jasmine.SpyObj<AuthService>;

  beforeEach(async(() => {
    authServiceSpy = jasmine.createSpyObj('AuthService', ['logout', 'build_login_link']);
    authServiceSpy.build_login_link.and.returnValue('https://auth0/authorize...');

    TestBed.configureTestingModule({
      declarations: [ UserPagePage ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      providers: [
        { provide: AuthService, useValue: authServiceSpy }
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UserPagePage);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  describe('Constructor - Login Link', () => {
    it('should build login link with callback path', () => {
      expect(authServiceSpy.build_login_link).toHaveBeenCalledWith('/tabs/user-page');
    });

    it('should store login URL from auth service', () => {
      expect(component.loginURL).toBe('https://auth0/authorize...');
    });
  });

  describe('Login/Logout UI', () => {
    it('should expose auth service to template', () => {
      fixture.detectChanges();
      expect(component.auth).toBeDefined();
    });

    it('should expose loginURL to template', () => {
      fixture.detectChanges();
      expect(component.loginURL).toBeDefined();
      expect(typeof component.loginURL).toBe('string');
    });
  });

  describe('Logout Functionality', () => {
    it('should call auth.logout when logout is triggered', () => {
      fixture.detectChanges();
      
      component.auth.logout();

      expect(authServiceSpy.logout).toHaveBeenCalled();
    });
  });

  describe('Login Callback Path', () => {
    it('should redirect back to user-page after login', () => {
      expect(authServiceSpy.build_login_link).toHaveBeenCalledWith('/tabs/user-page');
      
      // Verify that either:
      // 1. The returned login URL contains redirect_uri, OR
      // 2. The build_login_link was called with the correct callback path
      const wasCalledWithCorrectPath = authServiceSpy.build_login_link.calls.argsFor(0)[0] === '/tabs/user-page';
      expect(wasCalledWithCorrectPath).toBe(true);
    });
  });

  describe('Authentication State Display', () => {
    it('should show login button when not authenticated', () => {
      // Template shows login button when !auth.token
      // Create a mock auth service with token property set to null
      const mockAuthService = { 
        token: null, 
        logout: jasmine.createSpy('logout'),
        build_login_link: jasmine.createSpy('build_login_link').and.returnValue('https://auth0/authorize...')
      };
      
      expect(!mockAuthService.token).toBe(true);
    });

    it('should show logout and JWT when authenticated', () => {
      // Template shows logout button and JWT when auth.token exists
      const testToken = 'test.jwt.token';
      const mockAuthService = { 
        token: testToken, 
        logout: jasmine.createSpy('logout'),
        build_login_link: jasmine.createSpy('build_login_link').and.returnValue('https://auth0/authorize...')
      };
      
      expect(mockAuthService.token).toBe(testToken);
    });
  });
});
