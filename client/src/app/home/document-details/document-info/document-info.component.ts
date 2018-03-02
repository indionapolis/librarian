import { Component, HostListener, Inject, Input, OnInit } from '@angular/core';
import { DOCUMENT } from '@angular/platform-browser';
import { WINDOW } from "../../../shared/services/scroll.service";
import { Document as DocumentModel } from '../../../shared/models/documents.model';
import { $ } from 'protractor';
import { getUserRole } from '../../../auth/reducers/selectors';
import {UserService} from "../../../core/services/user.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-document-info',
  templateUrl: './document-info.component.html',
  styleUrls: ['./document-info.component.scss']
})
export class DocumentInfoComponent implements OnInit {
  @Input() document: DocumentModel;
  @Input() permission: boolean;
  thumbIsFixed: boolean;
  thumbWidth: number;
  description: string;
  constructor(
    @Inject(DOCUMENT) private documentEl: Document,
    @Inject(WINDOW) private window,
    private userService: UserService,
    private router: Router,
  ) { }

  bookDocument(documentId: number) {
    this.userService.bookTheDocument(documentId).subscribe(() => {
      this.router.navigate(['/user', 'orders'])
    });
  }

  ngOnInit() {
    this.description = this.document.description.substr(0, 200);
  }
  extendDescription($event) {
    this.description = this.document.description;
    $event.target.style.setProperty('display', 'none');
  }

  /*@HostListener("window:scroll", [])
  onWindowScroll() {
    let number = this.window.pageYOffset || this.documentEl.documentElement.scrollTop || this.documentEl.body.scrollTop || 0;
    if (number > 70 && this.description.length == this.document.description.length) {
      this.thumbIsFixed = true
    } else if (this.thumbIsFixed && number < 70) {
      this.thumbIsFixed = false;
    }
  }*/
}
