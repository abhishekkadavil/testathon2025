package api

import scala.concurrent.duration._

import io.gatling.core.Predef._
import io.gatling.http.Predef._

class EmployeeDepartmentSimulation extends Simulation {

  val baseUrl = "http://127.0.0.1:5000"

  val httpProtocol = http
    .baseUrl(baseUrl)
    .acceptHeader("application/json")
    .contentTypeHeader("application/json")

  val scn = scenario("Employee and Department API Test")
    .exec(
      http("Get Employee")
        .get("/employee")
        .check(status.is(200))
    )
    .pause(1)
    .exec(
      http("Get Department")
        .get("/department")
        .check(status.is(200))
    )

  setUp(
    scn.inject(
      constantUsersPerSec(5).during(10.seconds) // 5 RPS for 10 seconds
    )
  )
    .protocols(httpProtocol)
    .assertions(
      global.successfulRequests.percent.gt(95),        // Pass if >95% succeed
      global.responseTime.mean.lt(300),                // mean < 300ms
      global.responseTime.percentile4.lt(800)          // p99 < 800ms
    )
}
