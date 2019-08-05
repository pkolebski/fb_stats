from conversation import load_coversations
import matplotlib.pyplot as plt
from collections import Counter


def format_ranking(ranking, print_ranking=False, save_path=False):
    i = 0
    last = 1e1000
    formatted_ranking = []
    for name, count in ranking:
        if i > 0:
            if count != last:
                i += 1
        else:
            i += 1
        last = count
        formatted_ranking.append([i, [name, count]])
        if print_ranking:
            print(f'{i}: {name} - {count} messages')
    return formatted_ranking


def get_conversations_ranking(conversations, top=None, exclude=None, minimum=10):
    assert exclude in [None, 'Regular', 'Group'], "exclude argument should be None, 'Regular' or 'Group'"

    ranking = Counter({conv.title: len(conv) for conv in conversations if
                       conv.thread_type != exclude and
                       conv.is_still_participant and len(conv) >= minimum}).most_common(top)
    return ranking


def plot_ranking(ax, ranking, show=False):
    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(3, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', rotation=35)
    x = [name for i, [name, count] in ranking]
    rect = plt.bar(range(len(x)), [count for i, [name, count] in ranking])
    plt.xticks(range(len(x)), labels=x, rotation=-35, ha='left')
    autolabel(rect)
    # ax1.set_xticklabels(x, rotation=-45, ha='left')
    if show:
        plt.show()


conversations = load_coversations('messages/inbox')
ranking_regular = get_conversations_ranking(conversations, exclude='Group', top=10)
ranking_group = get_conversations_ranking(conversations, exclude='Regular', top=10)
ranking_all = get_conversations_ranking(conversations, top=10)
ranking_regular = format_ranking(ranking_regular, False)
ranking_group = format_ranking(ranking_group, False)
ranking_all = format_ranking(ranking_all, False)

fig = plt.figure(figsize=(20, 8))
ax1 = fig.add_subplot(1, 3, 1)
ax1.set_title('Regular chats')
plot_ranking(ax1, ranking_regular)
ax2 = fig.add_subplot(1, 3, 2, sharey=ax1)
ax2.set_title('Group chats')
plot_ranking(ax2, ranking_group)
ax3 = fig.add_subplot(1, 3, 3, sharey=ax1)
ax3.set_title('All chats')
plot_ranking(ax3, ranking_all)
plt.show()
