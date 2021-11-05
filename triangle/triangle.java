import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.stream.IntStream;

import static java.lang.Math.max;

class Scratch {
  public static void main(String[] args) throws IOException {
    BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(System.in));

    int depth = Integer.parseInt(bufferedReader.readLine().trim());
    String triangleContent = bufferedReader.readLine().trim();

    int[][] triangle =
        IntStream.range(0, depth).mapToObj(i -> IntStream.range(0, i + 1).map(j -> 0).toArray()).toArray(int[][]::new);

    int i = 0, j = 0;
    for (String row : triangleContent.split("\\|")) {
      row = row.trim();
      j = 0;
      for (String number : row.split(" ")) {
        triangle[i][j] = Integer.parseInt(number);
        j++;
      }
      i++;
    }

    int result = Result.getMaxSum(triangle);
    System.out.println(result);
  }

  static class Result {

    /*
     * Complete the 'get_max_sum' function below.
     *
     * The function is expected to return an INTEGER.
     * The function accepts 2D_INTEGER_ARRAY triangle as parameter.
     */

    public static int getMaxSum(int[][] triangle) {
      int[] result = IntStream.range(0, triangle.length).map(i -> 0).toArray();
      final int[] solve = solve(result, triangle, 0);
      return Arrays.stream(solve).max().orElse(-1);
    }

    private static int[] solve(int[] result, int[][] triangle, int currentIndex) {
      final int[] currentRow = triangle[currentIndex];

      currentRow[0] += result[0];
      for (int i = 1; i < currentRow.length; i++) {
        currentRow[i] += max(result[i - 1], result[i]);
      }

      for (int i = 0; i < currentRow.length; i++) {
        result[i] = currentRow[i];
      }

      if (currentRow.length == triangle.length) {
        return result;
      }
      currentIndex++;
      return solve(result, triangle, currentIndex);
    }
  }
}
