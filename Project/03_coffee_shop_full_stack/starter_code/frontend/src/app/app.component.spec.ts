import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { TestBed, async } from '@angular/core/testing';

import { Platform } from '@ionic/angular';
import { SplashScreen } from '@ionic-native/splash-screen/ngx';
import { StatusBar } from '@ionic-native/status-bar/ngx';

import { AppComponent } from './app.component';
import { AuthService } from './services/auth.service';

describe('AppComponent', () => {

  let statusBarSpy, splashScreenSpy, platformReadySpy, platformSpy, authServiceSpy;

  beforeEach(async(() => {
    statusBarSpy = jasmine.createSpyObj('StatusBar', ['styleDefault']);
    splashScreenSpy = jasmine.createSpyObj('SplashScreen', ['hide']);
    platformReadySpy = Promise.resolve();
    platformSpy = jasmine.createSpyObj('Platform', { ready: platformReadySpy });
    authServiceSpy = jasmine.createSpyObj('AuthService', ['load_jwts', 'check_token_fragment']);

    TestBed.configureTestingModule({
      declarations: [AppComponent],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      providers: [
        { provide: StatusBar, useValue: statusBarSpy },
        { provide: SplashScreen, useValue: splashScreenSpy },
        { provide: Platform, useValue: platformSpy },
        { provide: AuthService, useValue: authServiceSpy },
      ],
    }).compileComponents();
  }));

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.debugElement.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should initialize the app', async () => {
    TestBed.createComponent(AppComponent);
    expect(platformSpy.ready).toHaveBeenCalled();
    await platformReadySpy;
    expect(statusBarSpy.styleDefault).toHaveBeenCalled();
    expect(splashScreenSpy.hide).toHaveBeenCalled();
  });

  it('should load JWTs from storage on initialization', async () => {
    TestBed.createComponent(AppComponent);
    await platformReadySpy;
    expect(authServiceSpy.load_jwts).toHaveBeenCalled();
  });

  it('should check token fragment on initialization', async () => {
    TestBed.createComponent(AppComponent);
    await platformReadySpy;
    expect(authServiceSpy.check_token_fragment).toHaveBeenCalled();
  });

  it('should call load_jwts before check_token_fragment', async () => {
    const callOrder = [];
    authServiceSpy.load_jwts.and.callFake(() => callOrder.push('load_jwts'));
    authServiceSpy.check_token_fragment.and.callFake(() => callOrder.push('check_token_fragment'));

    TestBed.createComponent(AppComponent);
    await platformReadySpy;

    expect(callOrder).toEqual(['load_jwts', 'check_token_fragment']);
  });

});
