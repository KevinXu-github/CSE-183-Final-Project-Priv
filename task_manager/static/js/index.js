"use strict";

function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

let app = {};

app.config = {
  data: function() {
    return {
      posts: [],
      tags: [],
    };
  },
  methods: {
    add_post: function() {
      if (this.new_post) {
        fetch("/tagged_posts/api/posts", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ content: this.new_post }),
        })
          .then(response => response.json())
          .then(data => {
            console.log("created id:", data.id);
            app.load_data();
          });
      }
    },
    filter_tag: function(tag) {
      fetch("/tagged_posts/api/posts?tag=" + tag)
        .then(response => response.json())
        .then(data => {
          app.vue.posts = data.posts;
        });
    },
    delete_post: function(postId) {
      this.posts = this.posts.filter(post => post.id != postId);
      fetch("/tagged_posts/api/posts/" + postId, {
        method: "DELETE",
      })
        .then(response => response.json())
        .then(data => {
          app.load_data();
        });
    },
  },
};

app.load_data = function() {
  // GET data from db and store it into app.vue.data
  fetch("/tagged_posts/api/posts")
    .then(response => response.json())
    .then(data => {
      app.vue.posts = data.posts;
    });
  fetch("/tagged_posts/api/tags")
    .then(response => response.json())
    .then(data => {
      app.vue.tags = data.tags;
    });
};

app.vue = Vue.createApp(app.config).mount("#app");
app.load_data();
