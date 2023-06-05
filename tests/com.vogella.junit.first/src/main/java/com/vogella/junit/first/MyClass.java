package com.vogella.junit.first;

public class MyClass {
    // the following is just an example
  public int multiply(int x, int y) {
    if (x > 999) {
      throw new IllegalArgumentException("X should be less than 1000");
    }
    return x * y;
  }
  
  public int divide(int x, int y) {
	  return 0;
  }
  
  public int add(int x, int y) {
	  return 0;
  }
  
}