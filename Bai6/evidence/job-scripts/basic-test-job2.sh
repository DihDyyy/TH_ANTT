set -e
set -x
echo "This job tests something, but takes more time than test-job1."
echo "After the echo commands complete, it runs the sleep command for 20 seconds"
echo "which simulates a test that runs 20 seconds longer than test-job1"
sleep 20
