import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ModalController } from '@ionic/angular';
import { DrinkMenuPage } from './drink-menu.page';
import { DrinksService, Drink } from 'src/app/services/drinks.service';
import { AuthService } from 'src/app/services/auth.service';

describe('DrinkMenuPage', () => {
  let component: DrinkMenuPage;
  let fixture: ComponentFixture<DrinkMenuPage>;
  let drinksServiceSpy: jasmine.SpyObj<DrinksService>;
  let authServiceSpy: jasmine.SpyObj<AuthService>;
  let modalControllerSpy: jasmine.SpyObj<ModalController>;

  beforeEach(async(() => {
    drinksServiceSpy = jasmine.createSpyObj('DrinksService', ['getDrinks']);
    (drinksServiceSpy as any).items = {};  // Add items property to spy
    authServiceSpy = jasmine.createSpyObj('AuthService', ['can']);
    modalControllerSpy = jasmine.createSpyObj('ModalController', ['create']);

    TestBed.configureTestingModule({
      declarations: [ DrinkMenuPage ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      providers: [
        { provide: DrinksService, useValue: drinksServiceSpy },
        { provide: AuthService, useValue: authServiceSpy },
        { provide: ModalController, useValue: modalControllerSpy },
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DrinkMenuPage);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should load drinks on initialization', () => {
    fixture.detectChanges();
    expect(drinksServiceSpy.getDrinks).toHaveBeenCalled();
  });

  describe('openForm - Permission Gating', () => {
    it('should not open form when user lacks get:drinks-detail permission', async () => {
      authServiceSpy.can.and.returnValue(false);
      fixture.detectChanges();

      const drink: Drink = { id: 1, title: 'Test', recipe: [] };
      await component.openForm(drink);

      expect(modalControllerSpy.create).not.toHaveBeenCalled();
    });

    it('should open form when user has get:drinks-detail permission', async () => {
      authServiceSpy.can.and.returnValue(true);
      const mockModal = jasmine.createSpyObj('Modal', ['present']);
      modalControllerSpy.create.and.returnValue(Promise.resolve(mockModal));

      fixture.detectChanges();

      const drink: Drink = { id: 1, title: 'Test Drink', recipe: [] };
      await component.openForm(drink);

      expect(modalControllerSpy.create).toHaveBeenCalled();
      expect(mockModal.present).toHaveBeenCalled();
    });

    it('should allow opening form for new drink (null parameter) when authorized', async () => {
      authServiceSpy.can.and.returnValue(true);
      const mockModal = jasmine.createSpyObj('Modal', ['present']);
      modalControllerSpy.create.and.returnValue(Promise.resolve(mockModal));

      fixture.detectChanges();

      await component.openForm();

      expect(modalControllerSpy.create).toHaveBeenCalled();
      expect(mockModal.present).toHaveBeenCalled();
    });

    it('should prevent opening form for new drink when unauthorized', async () => {
      authServiceSpy.can.and.returnValue(false);
      fixture.detectChanges();

      await component.openForm();

      expect(modalControllerSpy.create).not.toHaveBeenCalled();
    });
  });

  describe('openForm - Modal Configuration', () => {
    beforeEach(() => {
      authServiceSpy.can.and.returnValue(true);
    });

    it('should pass existing drink to modal', async () => {
      const mockModal = jasmine.createSpyObj('Modal', ['present']);
      modalControllerSpy.create.and.returnValue(Promise.resolve(mockModal));

      fixture.detectChanges();

      const drink: Drink = {
        id: 1,
        title: 'Matcha',
        recipe: [{ name: 'matcha', color: 'green', parts: 1 }]
      };

      await component.openForm(drink);

      expect(modalControllerSpy.create).toHaveBeenCalledWith(
        jasmine.objectContaining({
          componentProps: jasmine.objectContaining({
            drink: drink,
            isNew: false
          })
        })
      );
    });

    it('should mark form as new when no drink provided', async () => {
      const mockModal = jasmine.createSpyObj('Modal', ['present']);
      modalControllerSpy.create.and.returnValue(Promise.resolve(mockModal));

      fixture.detectChanges();

      await component.openForm();

      expect(modalControllerSpy.create).toHaveBeenCalledWith(
        jasmine.objectContaining({
          componentProps: jasmine.objectContaining({
            drink: null,
            isNew: true
          })
        })
      );
    });

    it('should use DrinkFormComponent for modal', async () => {
      const mockModal = jasmine.createSpyObj('Modal', ['present']);
      modalControllerSpy.create.and.returnValue(Promise.resolve(mockModal));

      fixture.detectChanges();

      const drink: Drink = { id: 1, title: 'Test', recipe: [] };
      await component.openForm(drink);

      expect(modalControllerSpy.create).toHaveBeenCalledWith(
        jasmine.objectContaining({
          component: jasmine.anything()
        })
      );
    });
  });

  describe('UI Integration', () => {
    it('should expose Object to template for ngFor', () => {
      expect(component.Object).toBeDefined();
    });

    it('should expose drinks service to template', () => {
      fixture.detectChanges();
      expect(component.drinks).toBeDefined();
    });

    it('should have drinks service with items', () => {
      fixture.detectChanges();
      expect(component.drinks.items).toBeDefined();
    });
  });
});
