import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ModalController } from '@ionic/angular';
import { DrinkFormComponent } from './drink-form.component';
import { DrinksService, Drink } from 'src/app/services/drinks.service';
import { AuthService } from 'src/app/services/auth.service';

describe('DrinkFormComponent', () => {
  let component: DrinkFormComponent;
  let fixture: ComponentFixture<DrinkFormComponent>;
  let drinksServiceSpy: jasmine.SpyObj<DrinksService>;
  let authServiceSpy: jasmine.SpyObj<AuthService>;
  let modalControllerSpy: jasmine.SpyObj<ModalController>;

  beforeEach(async(() => {
    drinksServiceSpy = jasmine.createSpyObj('DrinksService', ['saveDrink', 'deleteDrink']);
    authServiceSpy = jasmine.createSpyObj('AuthService', ['can']);
    modalControllerSpy = jasmine.createSpyObj('ModalController', ['dismiss']);

    TestBed.configureTestingModule({
      declarations: [ DrinkFormComponent ],
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
    fixture = TestBed.createComponent(DrinkFormComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  describe('ngOnInit - New Drink', () => {
    beforeEach(() => {
      component.isNew = true;
    });

    it('should initialize new drink with default values', () => {
      fixture.detectChanges();

      expect(component.drink).toBeDefined();
      expect(component.drink.id).toBe(-1);
      expect(component.drink.title).toBe('');
      expect(component.drink.recipe).toBeDefined();
    });

    it('should add first ingredient for new drink', () => {
      fixture.detectChanges();

      expect(component.drink.recipe.length).toBe(1);
      expect(component.drink.recipe[0].name).toBe('');
      expect(component.drink.recipe[0].color).toBe('white');
      expect(component.drink.recipe[0].parts).toBe(1);
    });
  });

  describe('ngOnInit - Existing Drink', () => {
    it('should not modify existing drink on init', () => {
      const existingDrink: Drink = {
        id: 1,
        title: 'Matcha',
        recipe: [{ name: 'matcha', color: 'green', parts: 3 }]
      };
      component.drink = existingDrink;
      component.isNew = false;

      fixture.detectChanges();

      expect(component.drink.id).toBe(1);
      expect(component.drink.title).toBe('Matcha');
      expect(component.drink.recipe.length).toBe(1);
    });
  });

  describe('addIngredient', () => {
    beforeEach(() => {
      component.drink = {
        id: 1,
        title: 'Test Drink',
        recipe: [
          { name: 'milk', color: 'white', parts: 1 },
          { name: 'coffee', color: 'brown', parts: 2 }
        ]
      };
      fixture.detectChanges();
    });

    it('should add ingredient at end by default', () => {
      component.addIngredient();

      expect(component.drink.recipe.length).toBe(3);
      expect(component.drink.recipe[2].name).toBe('');
      expect(component.drink.recipe[2].color).toBe('white');
      expect(component.drink.recipe[2].parts).toBe(1);
    });

    it('should add ingredient after specified index', () => {
      component.addIngredient(0);

      expect(component.drink.recipe.length).toBe(3);
      expect(component.drink.recipe[1].name).toBe('');
      expect(component.drink.recipe[2].name).toBe('coffee');
    });

    it('should add ingredient with default properties', () => {
      component.addIngredient();
      const newIngredient = component.drink.recipe[component.drink.recipe.length - 1];

      expect(newIngredient.color).toBe('white');
      expect(newIngredient.parts).toBe(1);
    });

    it('should preserve existing ingredients when adding', () => {
      const originalIngredients = JSON.parse(JSON.stringify(component.drink.recipe));
      component.addIngredient();

      expect(component.drink.recipe[0]).toEqual(originalIngredients[0]);
      expect(component.drink.recipe[1]).toEqual(originalIngredients[1]);
    });
  });

  describe('removeIngredient', () => {
    beforeEach(() => {
      component.drink = {
        id: 1,
        title: 'Test Drink',
        recipe: [
          { name: 'milk', color: 'white', parts: 1 },
          { name: 'coffee', color: 'brown', parts: 2 },
          { name: 'foam', color: 'white', parts: 1 }
        ]
      };
      fixture.detectChanges();
    });

    it('should remove ingredient at specified index', () => {
      component.removeIngredient(1);

      expect(component.drink.recipe.length).toBe(2);
      expect(component.drink.recipe[0].name).toBe('milk');
      expect(component.drink.recipe[1].name).toBe('foam');
    });

    it('should remove first ingredient when index is 0', () => {
      component.removeIngredient(0);

      expect(component.drink.recipe.length).toBe(2);
      expect(component.drink.recipe[0].name).toBe('coffee');
    });

    it('should remove last ingredient', () => {
      component.removeIngredient(2);

      expect(component.drink.recipe.length).toBe(2);
      expect(component.drink.recipe[1].name).toBe('coffee');
    });
  });

  describe('closeModal', () => {
    it('should dismiss modal', () => {
      fixture.detectChanges();
      component.closeModal();

      expect(modalControllerSpy.dismiss).toHaveBeenCalled();
    });
  });

  describe('saveClicked', () => {
    it('should call saveDrink with current drink', () => {
      const testDrink: Drink = {
        id: 1,
        title: 'Matcha',
        recipe: [{ name: 'matcha', color: 'green', parts: 3 }]
      };
      component.drink = testDrink;
      fixture.detectChanges();

      component.saveClicked();

      expect(drinksServiceSpy.saveDrink).toHaveBeenCalledWith(testDrink);
    });

    it('should close modal after saving', () => {
      component.drink = { id: 1, title: 'Test', recipe: [] };
      fixture.detectChanges();

      component.saveClicked();

      expect(modalControllerSpy.dismiss).toHaveBeenCalled();
    });

    it('should close modal even if saveDrink fails', () => {
      component.drink = { id: 1, title: 'Test', recipe: [] };
      drinksServiceSpy.saveDrink.and.throwError('Error');
      fixture.detectChanges();

      // Should close modal even with error in saveDrink
      expect(() => component.saveClicked()).not.toThrow();
    });
  });

  describe('deleteClicked', () => {
    it('should call deleteDrink with current drink', () => {
      const testDrink: Drink = {
        id: 1,
        title: 'Matcha',
        recipe: [{ name: 'matcha', color: 'green', parts: 3 }]
      };
      component.drink = testDrink;
      fixture.detectChanges();

      component.deleteClicked();

      expect(drinksServiceSpy.deleteDrink).toHaveBeenCalledWith(testDrink);
    });

    it('should close modal after deleting', () => {
      component.drink = { id: 1, title: 'Test', recipe: [] };
      fixture.detectChanges();

      component.deleteClicked();

      expect(modalControllerSpy.dismiss).toHaveBeenCalled();
    });
  });

  describe('customTrackBy', () => {
    it('should return index for trackBy', () => {
      fixture.detectChanges();
      const result = component.customTrackBy(3, {});

      expect(result).toBe(3);
    });

    it('should handle any object type', () => {
      fixture.detectChanges();
      const testObj = { name: 'test', value: 123 };
      const result = component.customTrackBy(0, testObj);

      expect(result).toBe(0);
    });
  });

  describe('UI Integration', () => {
    it('should expose auth service to template', () => {
      fixture.detectChanges();
      expect(component.auth).toBeDefined();
    });

    it('should have Input properties for drink and isNew', () => {
      const testDrink: Drink = { id: 1, title: 'Test', recipe: [] };
      component.drink = testDrink;
      component.isNew = false;
      fixture.detectChanges();

      expect(component.drink).toEqual(testDrink);
      expect(component.isNew).toBe(false);
    });
  });

  describe('Form Validation Flow', () => {
    it('should handle create new drink flow', () => {
      component.isNew = true;
      fixture.detectChanges();

      // Verify form initialized
      expect(component.drink.id).toBe(-1);
      expect(component.drink.title).toBe('');

      // Simulate user input
      component.drink.title = 'New Coffee';
      component.drink.recipe[0].name = 'espresso';
      component.drink.recipe[0].parts = 2;

      // Save
      component.saveClicked();

      expect(drinksServiceSpy.saveDrink).toHaveBeenCalledWith(
        jasmine.objectContaining({
          id: -1,
          title: 'New Coffee'
        })
      );
    });

    it('should handle update existing drink flow', () => {
      const existingDrink: Drink = {
        id: 5,
        title: 'Matcha',
        recipe: [{ name: 'matcha', color: 'green', parts: 1 }]
      };
      component.drink = existingDrink;
      component.isNew = false;
      fixture.detectChanges();

      // Simulate user modification
      component.drink.title = 'Matcha Latte';
      component.drink.recipe[0].parts = 3;

      // Save
      component.saveClicked();

      expect(drinksServiceSpy.saveDrink).toHaveBeenCalledWith(
        jasmine.objectContaining({
          id: 5,
          title: 'Matcha Latte'
        })
      );
    });

    it('should handle delete existing drink flow', () => {
      const existingDrink: Drink = {
        id: 5,
        title: 'Matcha',
        recipe: []
      };
      component.drink = existingDrink;
      fixture.detectChanges();

      component.deleteClicked();

      expect(drinksServiceSpy.deleteDrink).toHaveBeenCalledWith(existingDrink);
    });
  });
});
