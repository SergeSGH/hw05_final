import time

from posts.models import Group, Post


def posts_create(
    cls, posts_number, group_post_number,
    test_group, test_slug,
    test_description, test_post_text
):
    for i in range(1, posts_number + 1):
        if i == 1:
            pr_current_group = 0
        current_group = i // (group_post_number + 1) + 1
        if current_group != pr_current_group:
            cls.group = Group.objects.create(
                title=test_group + str(current_group),
                slug=test_slug + str(current_group),
                description=test_description + str(current_group),
            )
        pr_current_group = current_group

        cls.post = Post.objects.create(
            author=cls.user,
            text=(test_post_text + str(i)),
            group=cls.group
        )

        time.sleep(0.000001)
