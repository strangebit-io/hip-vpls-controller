<template>
  <div class="main_content">
    <div class="about-div">
      HIP-VPLS switch configuration tool &#169; Strangebit. All rights reserved
    </div>
  </div>
</template>

<script>
export default {
  name: "About",
  data() {
    return {};
  },
  methods: {},
  components: {},
};
</script>

<style scoped>
h3 {
  color: black;
  text-align: center;
}

.about-div {
  position: absolute;

  width: 450px;
  height: 300px;

  /* Center form on page horizontally & vertically */
  position: absolute;
  top: 50%;
  left: calc(50% - 300px);
  width: 600px;
  margin: auto;
}

.login-form {
  width: 450px;
  height: 300px;

  background: white;
  border-radius: 10px;

  margin: 0;
  padding: 0;
}
</style>
