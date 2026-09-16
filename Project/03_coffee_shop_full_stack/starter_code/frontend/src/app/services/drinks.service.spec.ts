import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { DrinksService, Drink } from './drinks.service';
import { AuthService } from './auth.service';
import { environment } from 'src/environments/environment';

describe('DrinksService', () => {
  let service: DrinksService;
  let httpMock: HttpTestingController;
  let authService: jasmine.SpyObj<AuthService>;

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['can', 'activeJWT']);

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        DrinksService,
        { provide: AuthService, useValue: authServiceSpy }
      ]
    });

    service = TestBed.get(DrinksService);
    httpMock = TestBed.get(HttpTestingController);
    authService = TestBed.get(AuthService);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('getHeaders', () => {
    it('should return headers with Authorization Bearer token', () => {
      const testToken = 'test.jwt.token';
      authService.activeJWT.and.returnValue(testToken);

      const headers = service.getHeaders();

      expect(headers.headers.get('Authorization')).toBe(`Bearer ${testToken}`);
    });

    it('should include Bearer prefix', () => {
      const testToken = 'test.jwt.token';
      authService.activeJWT.and.returnValue(testToken);

      const headers = service.getHeaders();

      expect(headers.headers.get('Authorization')).toContain('Bearer ');
    });
  });

  describe('getDrinks', () => {
    it('should fetch drinks-detail when user has get:drinks-detail permission', (done) => {
      authService.can.and.returnValue(true);
      authService.activeJWT.and.returnValue('test.token');

      const mockResponse = {
        success: true,
        drinks: [
          {
            id: 1,
            title: 'Matcha Shake',
            recipe: [{ name: 'milk', color: 'grey', parts: 1 }]
          }
        ]
      };

      service.getDrinks();

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks-detail');
      expect(req.request.method).toBe('GET');
      expect(req.request.headers.get('Authorization')).toContain('Bearer');

      req.flush(mockResponse);

      expect(service.items[1]).toBeDefined();
      expect(service.items[1].title).toBe('Matcha Shake');
      done();
    });

    it('should fetch /drinks when user lacks get:drinks-detail permission', (done) => {
      authService.can.and.returnValue(false);
      authService.activeJWT.and.returnValue('test.token');

      const mockResponse = {
        success: true,
        drinks: [
          {
            id: 1,
            title: 'Matcha Shake',
            recipe: []
          }
        ]
      };

      service.getDrinks();

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks');
      expect(req.request.method).toBe('GET');

      req.flush(mockResponse);

      expect(service.items[1]).toBeDefined();
      done();
    });

    it('should populate items dictionary from response', (done) => {
      authService.can.and.returnValue(true);
      authService.activeJWT.and.returnValue('test.token');

      const mockResponse = {
        success: true,
        drinks: [
          { id: 1, title: 'Drink 1', recipe: [] },
          { id: 2, title: 'Drink 2', recipe: [] },
          { id: 3, title: 'Drink 3', recipe: [] }
        ]
      };

      service.getDrinks();

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks-detail');
      req.flush(mockResponse);

      expect(Object.keys(service.items).length).toBe(3);
      expect(service.items[1].title).toBe('Drink 1');
      expect(service.items[2].title).toBe('Drink 2');
      expect(service.items[3].title).toBe('Drink 3');
      done();
    });

    it('should handle empty drinks response', (done) => {
      authService.can.and.returnValue(true);
      authService.activeJWT.and.returnValue('test.token');

      const mockResponse = {
        success: true,
        drinks: []
      };

      service.getDrinks();

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks-detail');
      req.flush(mockResponse);

      expect(Object.keys(service.items).length).toBe(0);
      done();
    });
  });

  describe('saveDrink', () => {
    it('should PATCH existing drink (drink with id >= 0)', (done) => {
      authService.activeJWT.and.returnValue('test.token');

      const existingDrink: Drink = {
        id: 1,
        title: 'Updated Matcha Shake',
        recipe: [{ name: 'milk', color: 'grey', parts: 2 }]
      };

      const mockResponse = {
        success: true,
        drinks: [existingDrink]
      };

      service.saveDrink(existingDrink);

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks/1');
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual(existingDrink);

      req.flush(mockResponse);

      expect(service.items[1]).toBeDefined();
      expect(service.items[1].title).toBe('Updated Matcha Shake');
      done();
    });

    it('should POST new drink (drink with id < 0)', (done) => {
      authService.activeJWT.and.returnValue('test.token');

      const newDrink: Drink = {
        id: -1,
        title: 'New Coffee',
        recipe: [{ name: 'coffee', color: 'brown', parts: 1 }]
      };

      const mockResponse = {
        success: true,
        drinks: [{ ...newDrink, id: 4 }]
      };

      service.saveDrink(newDrink);

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newDrink);

      req.flush(mockResponse);

      expect(service.items[4]).toBeDefined();
      done();
    });

    it('should include Authorization header when saving', (done) => {
      authService.activeJWT.and.returnValue('test.token.with.signature');

      const drink: Drink = {
        id: 1,
        title: 'Test Drink',
        recipe: []
      };

      service.saveDrink(drink);

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks/1');
      expect(req.request.headers.get('Authorization')).toContain('Bearer test.token.with.signature');

      req.flush({ success: true, drinks: [drink] });
      done();
    });

    it('should handle POST failure gracefully', (done) => {
      authService.activeJWT.and.returnValue('test.token');

      const newDrink: Drink = {
        id: -1,
        title: 'New Drink',
        recipe: []
      };

      service.saveDrink(newDrink);

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks');
      expect(req.request.method).toBe('POST');
      req.flush({ success: false, error: 'Invalid drink' }, { status: 400, statusText: 'Bad Request' });

      done();
    });

    it('should handle PATCH failure gracefully', (done) => {
      authService.activeJWT.and.returnValue('test.token');

      const drink: Drink = {
        id: 1,
        title: 'Update',
        recipe: []
      };

      service.saveDrink(drink);

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks/1');
      expect(req.request.method).toBe('PATCH');
      req.flush({ success: false, error: 'Not found' }, { status: 404, statusText: 'Not Found' });

      done();
    });

    it('should only update items when success is true', (done) => {
      authService.activeJWT.and.returnValue('test.token');

      const drink: Drink = {
        id: 1,
        title: 'Test',
        recipe: []
      };

      service.saveDrink(drink);

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks/1');
      req.flush({ success: false, drinks: [] });

      expect(service.items[1]).toBeUndefined();
      done();
    });
  });

  describe('deleteDrink', () => {
    it('should remove drink from local items immediately', (done) => {
      authService.activeJWT.and.returnValue('test.token');
      const drink: Drink = {
        id: 1,
        title: 'Drink to Delete',
        recipe: []
      };

      service.items[1] = drink;
      service.deleteDrink(drink);

      expect(service.items[1]).toBeUndefined();
      
      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks/1');
      req.flush({});
      done();
    });

    it('should send DELETE request to correct endpoint', (done) => {
      authService.activeJWT.and.returnValue('test.token');

      const drink: Drink = {
        id: 2,
        title: 'Drink to Delete',
        recipe: []
      };

      service.items[2] = drink;
      service.deleteDrink(drink);

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks/2');
      expect(req.request.method).toBe('DELETE');

      req.flush({});
      done();
    });

    it('should include Authorization header in DELETE request', (done) => {
      authService.activeJWT.and.returnValue('test.jwt.token');

      const drink: Drink = {
        id: 3,
        title: 'Drink',
        recipe: []
      };

      service.items[3] = drink;
      service.deleteDrink(drink);

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks/3');
      expect(req.request.headers.get('Authorization')).toContain('Bearer test.jwt.token');

      req.flush({});
      done();
    });

    it('should handle DELETE failure gracefully', (done) => {
      authService.activeJWT.and.returnValue('test.token');

      const drink: Drink = {
        id: 4,
        title: 'Drink',
        recipe: []
      };

      service.items[4] = drink;
      service.deleteDrink(drink);

      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks/4');
      expect(req.request.method).toBe('DELETE');
      req.flush({ success: false }, { status: 404, statusText: 'Not Found' });

      // Item should already be removed locally
      expect(service.items[4]).toBeUndefined();
      done();
    });
  });

  describe('drinksToItems', () => {
    it('should add drinks to items dictionary', () => {
      const drinks: Drink[] = [
        { id: 1, title: 'Drink 1', recipe: [] },
        { id: 2, title: 'Drink 2', recipe: [] }
      ];

      service.drinksToItems(drinks);

      expect(service.items[1]).toBeDefined();
      expect(service.items[2]).toBeDefined();
    });

    it('should preserve existing items when adding new ones', () => {
      service.items[1] = { id: 1, title: 'Existing', recipe: [] };

      const newDrinks: Drink[] = [
        { id: 2, title: 'New', recipe: [] }
      ];

      service.drinksToItems(newDrinks);

      expect(service.items[1]).toBeDefined();
      expect(service.items[2]).toBeDefined();
    });

    it('should handle empty array', () => {
      const emptyDrinks: Drink[] = [];

      service.drinksToItems(emptyDrinks);

      expect(Object.keys(service.items).length).toBe(0);
    });

    it('should overwrite existing drink with same id', () => {
      service.items[1] = { id: 1, title: 'Old Title', recipe: [] };

      const updatedDrinks: Drink[] = [
        { id: 1, title: 'New Title', recipe: [{ name: 'milk', color: 'white', parts: 1 }] }
      ];

      service.drinksToItems(updatedDrinks);

      expect(service.items[1].title).toBe('New Title');
      expect(service.items[1].recipe.length).toBe(1);
    });
  });

  describe('integration scenarios', () => {
    it('should handle full CRUD flow for manager user', (done) => {
      authService.can.and.returnValue(true);
      authService.activeJWT.and.returnValue('manager.token');

      // Step 1: Get all drinks with detail
      const getDrinksResponse = {
        success: true,
        drinks: [
          { id: 1, title: 'Matcha', recipe: [{ name: 'matcha', color: 'green', parts: 1 }] }
        ]
      };

      service.getDrinks();
      let req = httpMock.expectOne(environment.apiServerUrl + '/drinks-detail');
      req.flush(getDrinksResponse);

      expect(service.items[1]).toBeDefined();

      // Step 2: Create new drink
      const newDrink: Drink = {
        id: -1,
        title: 'New Coffee',
        recipe: [{ name: 'coffee', color: 'brown', parts: 1 }]
      };

      service.saveDrink(newDrink);
      req = httpMock.expectOne(environment.apiServerUrl + '/drinks');
      req.flush({
        success: true,
        drinks: [{ ...newDrink, id: 2 }]
      });

      expect(service.items[2]).toBeDefined();

      // Step 3: Update drink
      const updatedDrink: Drink = {
        id: 2,
        title: 'Updated Coffee',
        recipe: [{ name: 'espresso', color: 'brown', parts: 2 }]
      };

      service.saveDrink(updatedDrink);
      req = httpMock.expectOne(environment.apiServerUrl + '/drinks/2');
      req.flush({
        success: true,
        drinks: [updatedDrink]
      });

      // Step 4: Delete drink
      service.deleteDrink(service.items[2]);
      req = httpMock.expectOne(environment.apiServerUrl + '/drinks/2');
      req.flush({});

      expect(service.items[2]).toBeUndefined();
      done();
    });

    it('should handle read-only flow for barista user', (done) => {
      authService.can.and.returnValue(false);
      authService.activeJWT.and.returnValue('barista.token');

      const getDrinksResponse = {
        success: true,
        drinks: [
          { id: 1, title: 'Matcha', recipe: [] }
        ]
      };

      service.getDrinks();
      const req = httpMock.expectOne(environment.apiServerUrl + '/drinks');
      req.flush(getDrinksResponse);

      expect(service.items[1]).toBeDefined();
      expect(service.items[1].recipe).toEqual([]);
      done();
    });
  });
});
