<template>
  <div>
      <h1 class="center">DEBUG Preprocessor</h1>
    <span>Please, sir/madam, write a sentence:</span>
    <br>
    <br>
    <div>
    <form method="post" v-on:submit.prevent="onSubmit" >
        <textarea v-model="text" placeholder="something?" rows="10" style="padding: 10px; border-color: #2c3e50; border-radius: 5px;width:90%;"></textarea>
        <br> <br>
        <div>
            <input id="select_all" type="checkbox" v-model="selectAll">
            <label for="select_all"><b>Select all</b></label>
        </div>
        <span v-for="f in functionalities" :key="'i_' + f.id">
            <input type="checkbox" v-model="selected" :id="'cb_' + f.id" :value="f.id">
            <label :for="'cb_' + f.id ">{{ f.message }}</label>
            &nbsp;
        </span>

        <br> <br>
        <button type="submit" name="button">Submit</button>
    </form>
    </div>
    <br><br>
    <p style="white-space: pre-line;" class ="code"><b>process (</b> {{ text }} <b>)</b></p>
    <div v-for="f in allResponded" :key="'res_' + f.id" class="code"><b>{{f.id}}</b><br>&darr;<br>{{f.response}}<br><br></div>
    <p id="processed_box" v-if="processed_sent" class="box"><b>{{processed_sent}}</b></p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
name: 'Home',
  data () {
    return {
        functionalities: [{
            'id': 'lower',
            'message': 'Lowercase',
            'response': ''
        }, {
            'id': 'abbreviations',
            'message': 'Expand',
            'response': ''
        }, {
            'id': 'spell',
            'message': 'Check Spelling',
            'response': ''
        }],
        selected : [],
        text: '',
        processed_sent : ""
    }
  },
    watch : {
        text: function() {
            this.functionalities.forEach(function(f) {
                f.response = ''
            });
            this.processed_sent = ''
        }
    },
  computed: {
      selectAll: {
            get: function () {
                return this.functionalities ? this.selected.length == this.functionalities.length : false;
            },
            set: function (value) {
                var selected = [];

                if (value) {
                    this.functionalities.forEach(function (f) {
                        selected.push(f.id);
                    });
                }
                this.selected = selected;
            }
        },
      allSelected : function() {
          return this.functionalities.filter(f => this.selected.includes(f.id));
      },
      allResponded : function() {
          return this.functionalities.filter(f => f.response !== '');
      }
  },
  methods: {
      toggleSelect() {
          var select = this.selectAll;
          this.functionalities.forEach(function(f) {
              f.checked = !select;
          });
          this.selectAll = !select;
      },
      onSubmit() {
          const url = 'http://localhost:7000/api/preprocess'

          console.log(this.text)
          var payload = {
              sentence: this.text,
              options: this.selected,
              verbose: true
          }
          var headers = {'Content-Type': 'application/json'}

          console.log(payload)
          axios.post(url, payload, headers).then((res) => {
              console.log(res)
              this.allSelected.forEach(function(f) {
                  f.response = res["data"]["debug"][f.id]
                  console.log(f.response)
              })
              this.processed_sent = res["data"]["processed"]
              }).catch((err) => {console.log(err);})
          console.log("finish")
            setTimeout(function() {
              document.getElementById('processed_box').scrollIntoView({ behavior: 'smooth' });
          }, 100);

      },
  }
}
</script>
