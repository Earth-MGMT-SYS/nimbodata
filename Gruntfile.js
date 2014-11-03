module.exports = function(grunt) {
  grunt.initConfig({
   nose: {
     options: {
      verbosity: 2, 
      rednose: true
     },
     src: ['test'] 
    },
 
    watch: {
      js: {
        options: {
          spawn: true,
          interrupt: true,
          debounceDelay: 250,
        },
        files: ['Gruntfile.js', '*.py', '**/*.py', '**/*.js', '**/**/*.js'],
        tasks: ['simplemocha','nose']
     }
    },
    simplemocha: {
      all: {src: ['core/static/jsclient/test/*.js'] }
    }
  });
 
  grunt.loadNpmTasks('grunt-nose');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-simple-mocha');
 
  grunt.registerTask('default', ['simplemocha','nose']);
  grunt.registerTask('wezigboo', 'watch');
 
};
