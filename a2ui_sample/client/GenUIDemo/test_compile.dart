import 'lib/main.dart' as app;

void main() {
  print('Testing GenUIDemo compilation...');
  try {
    app.main();
    print('App compiled successfully!');
  } catch (e) {
    print('Compilation error: $e');
  }
}
