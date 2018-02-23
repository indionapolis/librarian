import { Injectable } from '@angular/core';
import {
  Http,
  ConnectionBackend,
  RequestOptions,
  RequestOptionsArgs,
  Response,
  Headers,
  Request
} from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { AuthService } from './auth.service';
import { Subject } from 'rxjs/Subject';
import { environment } from "../../../environments/environment";
import { HttpErrorResponse } from '@angular/common/http';

@Injectable()
export class HttpService extends Http {
  public loading = new Subject<{loading: boolean, error: any}>();

  constructor(
    backend: ConnectionBackend,
    defaultOptions: RequestOptions,
  ) {
    super(backend, defaultOptions);


    this.loading.next({
      loading: true, error: null
    });
  }

  /**
   * Performs any type of http request.
   * @param url
   * @param options
   * @returns {Observable<Response>}
   */
  request(url: string | Request, options?: RequestOptionsArgs): Observable<Response> {
    return super.request(url, options)
  }

  /**
   * Performs a request with `get` http method.
   * @param url
   * @param options
   * @returns {Observable<>}
   */
  get(url: string, options?: RequestOptionsArgs): Observable<any> {
    this.requestInterceptor();
    return super.get(this.getFullUrl(url), this.requestOptions(options))
      //.delay(1000)
      .catch(this.onCatch.bind(this))
      .do((res: Response) => {
        this.onSubscribeSuccess(res);
      }, (error: any) => {
        this.onSubscribeError(error);
      })
      .finally(() => {
        this.onFinally();
      });
  }

  getLocal(url: string, options?: RequestOptionsArgs): Observable<any> {
    return super.get(url, options);
  }

  /**
   * Performs a request with `post` http method.
   * @param url
   * @param body
   * @param options
   * @returns {Observable<>}
   */
  post(url: string, body: any, options?: RequestOptionsArgs): Observable<any> {
    this.requestInterceptor();
    return super.post(this.getFullUrl(url), body, this.requestOptions(options))
      .catch(this.onCatch.bind(this))
      .do((res: Response) => {
        this.onSubscribeSuccess(res);
      }, (error: any) => {
        this.onSubscribeError(error);
      })
      .finally(() => {
        this.onFinally();
      });
  }

  /**
   * Performs a request with `put` http method.
   * @param url
   * @param body
   * @param options
   * @returns {Observable<>}
   */
  put(url: string, body: any, options?: RequestOptionsArgs): Observable<any> {
    this.requestInterceptor();
    return super.put(this.getFullUrl(url), body, this.requestOptions(options))
      .catch(this.onCatch.bind(this))
      .do((res: Response) => {
        this.onSubscribeSuccess(res);
      }, (error: any) => {
        this.onSubscribeError(error);
      })
      .finally(() => {
        this.onFinally();
      });
  }

  /**
   * Performs a request with `delete` http method.
   * @param url
   * @param options
   * @returns {Observable<>}
   */
  delete(url: string, options?: RequestOptionsArgs): Observable<any> {
    this.requestInterceptor();
    return super.delete(this.getFullUrl(url), this.requestOptions(options))
      .catch(this.onCatch.bind(this))
      .do((res: Response) => {
        this.onSubscribeSuccess(res);
      }, (error: any) => {
        this.onSubscribeError(error);
      })
      .finally(() => {
        this.onFinally();
      });
  }


  patch(url: string, options?: RequestOptionsArgs): Observable<any> {
    this.requestInterceptor();
    return super.patch(this.getFullUrl(url), this.requestOptions(options))
      .catch(this.onCatch.bind(this))
      .do((res: Response) => {
        this.onSubscribeSuccess(res);
      }, (error: any) => {
        this.onSubscribeError(error);
      })
      .finally(() => {
        this.onFinally();
      });
  }


  /**
   * Request options.
   * @param options
   * @returns {RequestOptionsArgs}
   */
  private requestOptions(options?: RequestOptionsArgs): RequestOptionsArgs {
    if (options == null) {
      options = new RequestOptions();
    }

    if (options.headers == null) {
      options.headers = new Headers();
    }
    const user = localStorage.getItem('user') != "undefined" ? JSON.parse(localStorage.getItem('user')) : null;
    const token = localStorage.getItem("token");
    options.headers.set('Content-Type', 'application/json');
    options.headers.set('Bearer', "JWT " + token);
    return options;
  }

  /**
   * Build API url.
   * @param url
   * @returns {string}
   */
  private getFullUrl(url: string): string {
    return environment.API_ENDPOINT + url;
  }

  /**
   * Request interceptor.
   */
  private requestInterceptor(): void {
    //console.log('Sending Request');
    // this.loaderService.showPreloader();
    this.loading.next({
      loading: true, error: null
    });
  }

  /**
   * Response interceptor.
   */
  private responseInterceptor(): void {
    //console.log('Request Complete');
    // this.loaderService.hidePreloader();
  }

  /**
   * Error handler.
   * @param error
   * @param caught
   * @returns {ErrorObservable}
   */
  private onCatch(error: any, caught: Observable<any>): Observable<any> {
    return Observable.of(error);
  }

  /**
   * onSubscribeSuccess
   * @param res
   */
  private onSubscribeSuccess(res: Response): void {
    this.loading.next({
      loading: false, error: null
    });
  }

  /**
   * onSubscribeError
   * @param error
   */
  private onSubscribeError(error: any): void {
    this.loading.next({
      loading: false, error: {
        ok: false,
        statusText: "Server error",
        _body: "[{'message': 'Could not connect to server.\n Please check your internet connection'}]"
      }
    });
  }

  /**
   * onFinally
   */
  private onFinally(): void {
    this.responseInterceptor();
  }
}
