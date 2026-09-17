import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-user-page',
  templateUrl: './user-page.page.html',
  styleUrls: ['./user-page.page.scss'],
})
export class UserPagePage implements OnInit {
  loginURL: string;

  constructor(public auth: AuthService) {
    // Use an Auth0-allowed callback route and redirect from there in app routing.
    this.loginURL = auth.build_login_link('/callback');
  }

  ngOnInit() {
  }

}
