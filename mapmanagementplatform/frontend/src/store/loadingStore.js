import { makeAutoObservable } from 'mobx';

class LoadingStore {
  isLoading = false;
  constructor() {
    makeAutoObservable(this);
  }

  setLoadingProcess(isLoading) {
    this.isLoading = isLoading;
  }

  get IsLoading() {
    return this.isLoading;
  }
}

const loadingStore = new LoadingStore();

export default loadingStore;
