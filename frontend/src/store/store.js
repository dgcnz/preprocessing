import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export const store = new Vuex.Store({
  state: {
    debugRaws: [],
    messages: []
  },
  mutations: {
    addMessage (state, Message) {
      state.messages.push(Message)
    },
    addDebugRaw (state, RawResponse) {
      state.debugRaws.push(RawResponse)
    }
  },
  getters: {
    debugRaws: state => state.debugRaws,
    messages: state => state.messages
  }
})
