import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { StoreModule } from '@ngrx/store';
import { RouterModule, PreloadAllModules } from '@angular/router';
import { AppComponent } from './app.component';
import { EffectsModule } from '@ngrx/effects';
import { routes } from './app.routes';
import { environment } from './../environments/environment.prod';

// Modules
import { SharedModule } from './shared/shared.module';
import { CoreModule } from './core/core.module';
import { AuthModule } from './auth/auth.module';
import { LayoutModule } from './layout/layout.module';
import { DocumentModule } from './document/document.module';
import { reducers, metaReducers } from './app.reducers';


import 'rxjs/add/operator/map';
import 'rxjs/add/operator/filter';
import 'rxjs/add/operator/switchMap';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/do';
import 'rxjs/add/operator/finally';
import 'rxjs/add/operator/shareReplay';
import 'rxjs/add/operator/withLatestFrom';
import 'rxjs/add/observable/of';
import 'rxjs/add/operator/delay';
import { DocumentEffects } from './document/reducers/document.effects';
import { LoaderComponent } from './shared/components/loader/loader.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { AdminModule } from './admin/admin.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    StoreModule.forRoot(reducers, { metaReducers }),
    StoreDevtoolsModule.instrument({
      maxAge: 25, // Retains last 25 states
      logOnly: environment.production // Restrict extension to log-only mode
    }),

    RouterModule.forRoot(routes, { preloadingStrategy: PreloadAllModules }),
    EffectsModule.forRoot([DocumentEffects]),
    NgbModule.forRoot(),

    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    HttpModule,
    LayoutModule,
    AdminModule,
    AuthModule,
    DocumentModule,
    CoreModule,
    SharedModule
  ],
  providers: [
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
